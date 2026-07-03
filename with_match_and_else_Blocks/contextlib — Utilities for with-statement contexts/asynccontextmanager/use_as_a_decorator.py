"""
Python 3.10 version থেকে @asynccontextmanager দিয়ে তৈরি করা ফাংশনগুলোকে সরাসরি অন্য কোনো asynchronous function এর উপরে decorator
হিসেবেও ব্যবহার করা যায়। যখন এটি ডекোরেটর হিসেবে ব্যবহৃত হয়, তখন প্রতিবার মূল ফাংশনটি কল করার সময় backend এ একটি নতুন generator instance
তৈরি হয়, যা একে একাধিকবার কল করার উপযোগী (reusable) করে তোলে।
"""

import asyncio
import time
from contextlib import asynccontextmanager

@asynccontextmanager
async def async_timer(label):
    start_time = time.monotonic()

    try:
        yield
    finally:
        end_time = time.monotonic()
        print(f"[{label}] Execution took {end_time - start_time:.4f} seconds.")


@async_timer("Heavy Network Task")
async def fetch_remote_api():
    print("Starting API request...")
    await asyncio.sleep(1)
    print("API request finished.")

async def main():
    await fetch_remote_api()

asyncio.run(main())

"""
Phase 1: ContextDecorator Integration (Compilation Time)

PART 1: Factory Object Creation

@async_timer("Heavy Network Task")
async def fetch_remote_api():
    ...

code compile হওয়ার সময় python সবার আগে decorator-এর অংশটুকু অর্থাৎ `async_timer("Heavy Network Task")` execute করে। এটি সরাসরি কোনো 
code run করে না বরং ব্যাকগ্রাউন্ডে `_AsyncGeneratorContextManager` ক্লাসের একটি object তৈরি করে। ধরা যাক, python internally এই অবজেক্টটিকে 
`temp` নামক একটি ভেরিয়েবলে সাময়িকভাবে জমা রাখে।

temp = async_timer("Heavy Network Task")

PART 2: Asynchronous `__call__` Execution
পাইথনের `_AsyncGeneratorContextManager` ক্লাসটি বেস ক্লাস `AbstractAsyncContextManager` থেকে decorator হিসেবে কাজ করার ক্ষমতা লাভ করে। এর 
ফলে অবজেক্টটি একটি callable অবজেক্টে পরিণত হয়। object তৈরি হওয়ার সাথে সাথে python internally নিচের অপারেশনটি চালায়:
        fetch_remote_api = temp.__call__(fetch_remote_api)

এখানে original `fetch_remote_api` ফাংশনটিকে argument হিসেবে `__call__` মেথডের ভেতরে pass করে দেওয়া হচ্ছে।

PART 3: Asynchronous Wrapper Injection
decorator অবজেক্টের ভেতরের `__call__` মেথডটি অরিজিনাল ফাংশনটিকে সরাসরি return করে না। এটি তার নিজের ভেতরে একটি সম্পূর্ণ নতুন এসিনক্রোনাস `inner` 
ফাংশন তৈরি করে এবং original ফাংশনটিকে তার ভেতরে একটি `async with` ব্লক দিয়ে wrap করে দেয়। এর internal code design মূলত এইরকম:

def __call__(self, func):
    
    async def inner(*args, **kwargs):
        async with self: 
            return await func(*args, **kwargs)
    return inner


PART 4: The Final Structure in Memory
উপরের প্রক্রিয়ার পর অরিজিনাল `fetch_remote_api` ফাংশনটি মেমোরিতে সম্পূর্ণ প্রতিস্থাপিত হয়ে ঐ `inner` ফাংশনের রূপ ধারণ করে। Compilation শেষে মেমোরিতে 
এর আসল structure দাঁড়ায় ঠিক এইরকম:

async def fetch_remote_api():
    async with temp: 
        print("Starting API request...")
        await asyncio.sleep(0.5)
        print("API request finished.")

                       ------------------------------------------------------------------------------
                    
Phase 2: Runtime Execution Lifecycle (The Deep-Dive Flow)
যখন মেইন প্রোগ্রাম থেকে `await fetch_remote_api()` লাইনটি call করা হয়, তখন মূলত মেমোরিতে থাকা রূপান্তরিত `inner` ফাংশনটি trigger হয় এবং 
নিচের life-cycle টি সম্পাদিত হয়:

PART 5: `async with` Block Initialization
Converted ফাংশনের ভেতরে প্রবেশ করার পর যখনই `async with temp:` লাইনটি encounter হয়, python সাথে সাথে ঐ decorator অবজেক্টের `__aenter__` 
মেথডটিকে `await` করে call করে। like : await manager.__aenter__()

PART 6: Asynchronous Generator Activation via `__aenter__`
পাইথনের internal `__aenter__` মেথডটি built-in `anext()` ফাংশন ব্যবহার করে, hand made function `async_timer` জেনারেটরটিকে প্রথমবার 
activate করে:

async def __aenter__(self):
    try:
        return await anext(self.gen)
    except StopAsyncIteration:
        raise RuntimeError("generator didn't yield") from None

এর ফলে জেনারেটর ফাংশনটি তার প্রথম লাইন থেকে এক্সিকিউট হওয়া শুরু করে এবং শুরুর সময়টি রেকর্ড করে:
        start_time = time.monotonic() সময় গণনা শুরু হলো


PART 7: The Yield Pause
জেনারেটরটি চলতে চলতে যখনই `try` ব্লকের ভেতরের `yield` keyword লাইনে পৌঁছায়, তখন জেনারেটরটি স্বভাবগতভাবেই তার মেমোরি state এবং `start_time` 
ভেরিয়েবল সহ সাময়িকভাবে pause হয়ে ওখানেই থমকে দাঁড়িয়ে থাকে। `__aenter__` মেথডের কাজ এখানে শেষ হয় এবং control আবার মূল ব্লকে ফিরে আসে।

PART 8: Function Body & Event Loop Interleaving
এবার অরিজিনাল ফাংশনের ভেতরের কোডগুলো একে একে রান হওয়া শুরু করে:

print("Starting API request...")
await asyncio.sleep(0.5) 
print("API request finished.")

যখন `await asyncio.sleep(0.5)` লাইনটি trigger হয়, তখন কারেন্ট task-টি সাময়িকভাবে inactive হয় এবং event loop অন্য কোনো ready task 
থাকলে তা execute করার সুযোগ পায়। এই 0.5 সেকেন্ড জুড়ে ব্যাকগ্রাউন্ডে জেনারেটর ফাংশনটি কিন্তু ঐ `yield` লাইনেই pause অবস্থায় স্থির থাকে।

PART 9: `async with` Block Exit
original ফাংশনের ভেতরের শেষ print statemant-এর কাজ শেষ হওয়া মাত্রই পাইথন `async with` ব্লক থেকে বের হওয়ার জন্য internally decorator 
অবজেক্টের `__aexit__` মেথডটিকে `await` করে call করে।

await manager.__aexit__(None, None, None)

PART 10: Generator Resumption inside `__aexit__`
যেহেতু ব্লকের ভেতরে কোনো error ঘটেনি, তাই `__aexit__` মেথডটি পুনরায় internally `anext()` call করে ঐ `yield` লাইনে pause হয়ে থাকা 
জেনারেটরটিকে আবার active করে:

async def __aexit__(self, type, value, traceback):
    if type is None:
        try:
            await anext(self.gen)
        except StopAsyncIteration:
            return True


PART 11: Finally Block Execution & Cleanup
জেনারেটরটি পুনরায় active হয়ে তার `yield` লাইনের ঠিক পরের অংশ অর্থাৎ `finally` ব্লকে প্রবেশ করে এবং অবশিষ্ট শেষ কোডটুকু এক্সিকিউট করে সম্পূর্ণ শেষ 
হয়ে যায়:

finally:
    end_time = time.monotonic()
    print(f"[Heavy Network Task] Execution took {end_time - start_time:.4f} seconds.")


PART 12: The `StopAsyncIteration` Termination
`finally` ব্লকের কাজ শেষ হওয়ার সাথে সাথে generator ফাংশনটির lifetime শেষ হয়ে যায় এবং python একটি internal `StopAsyncIteration` 
exception raise করে। `__aexit__` মেথডের ভেতরের build-in mechanism এই exception-টিকে নিঃশব্দে catch করে ফেলে, যার ফলে কোনো crash 
ছাড়াই পুরো decorator execution process টি সফলভাবে সম্পন্ন হয়।
"""
