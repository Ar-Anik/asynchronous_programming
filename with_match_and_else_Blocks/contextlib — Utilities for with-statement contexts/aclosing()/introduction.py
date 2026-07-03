"""
`contextlib.aclosing(thing)`
একটি async context manager return করে যা block-এর কাজ শেষ হওয়ার পর `thing` অবজেক্টটির `aclose()` method-টিকে call করে। এটি মূলত নিচের
কোডটির সমতুল্য:
"""

"""
from contextlib import asynccontextmanager

@asynccontextmanager
async def aclosing(thing):
    try:
        yield thing
    finally:
        await thing.aclose()
"""

"""
যদি কোনো ক্লাসের ভেতরে aclose() নামে একটি asynchronous function (coroutine) ডিফাইন করা থাকে, তবে async with aclosing(obj) ব্যবহার করলে 
with block-এর কাজ শেষ হওয়া মাত্রই পাইথন স্বয়ংক্রিয়ভাবে সেই aclose() function-টিকে await obj.aclose() করে কল করে দেয়।
"""

# Code Example: Safe Early Break in Async Generator
import asyncio
from contextlib import aclosing

async def real_time_data_stream():
    try:
        print('Stream Started: Resource Acquired.')
        for i in range(1, 10):
            await asyncio.sleep(1)
            yield i
    finally:
        print("Stream stopped: Resource safely released inside generator finally block.")


async def main():
    print('----------- Starting Async Iteration -----------')
    async with aclosing(real_time_data_stream()) as stream:
        async for value in stream:
            if value == 3:
                print("Condition met! Breaking the loop early.")
                break

    print('----------- Async Iteration Finished -----------')


asyncio.run(main())


"""
aclosing() asynchronous generators যখন কোনো `break` অথবা `exception` এর কারণে মাঝপথে হঠাৎ বন্ধ (early exit) হয়ে যায়, তখন তাদের 
deterministic (তাৎক্ষণিক ও সুনিশ্চিত) cleanup নিশ্চিত করে। উদাহরণস্বরূপ:
"""

async with aclosing(real_time_data_stream()) as stream:
    async for value in stream:
        if value == 3:
            print("Condition met! Breaking the loop early.")
            break

"""
এই প্যাটার্নটি নিশ্চিত করে যে, জেনারেটরের asynchronous exit code অর্থাৎ `finally` block ঠিক সেই একই context-এর ভেতরে execute হবে যেটির ভেতরে 
তার iteration-গুলো চলছিল (যাতে করে exception এবং context variables-গুলো প্রত্যাশা অনুযায়ী কাজ করতে পারে, এবং exit কোডটি যেন এমন কোনো 
task-এর lifetime শেষ হওয়ার পর run না হয় যার উপর সেটি নিজে নির্ভরশীল ছিল)।

1. Loop Break হলে CPython Garbage Collector (GC) এর স্বয়ংক্রিয় ভূমিকা
পাইথনের standard runtime engine (CPython) মূলত Reference Counting এর উপর ভিত্তি করে মেমোরি ম্যানেজমেন্ট করে। যখন কোনো কোডে `aclosing` 
ছাড়া সরাসরি লুপের লাইনে এসিনক্রোনাস জেনারেটর কল করা হয়:

async def main():
    async for value in my_generator():
        if value == 42:
            break

Step-1 (Reference drop): `break` execute হওয়া মাত্রই control `async for` লুপের বাইরে চলে যায়। যেহেতু `my_generator()` অবজেক্টটিকে বাইরে কোনো 
ভেরিয়েবলে স্টোর করে রাখা হয়নি, তাই লুপ থেকে বের হওয়ার সাথে সাথেই মেমোরিতে এই জেনারেটর অবজেক্টটির reference count কমে সরাসরি Zero(0) হয়ে যায়।

Step-2 (GC Activation): reference count Zero হওয়া মাত্রই CPython-এর Garbage Collector মেমোরি থেকে অবজেক্টটিকে ধ্বংস (deallocate) করার 
প্রক্রিয়া শুরু করে এবং অবজেক্টের ইন্টারনাল `__del__` মেথড trigger হয়।

Step-3 (aclose Scheduling): অবজেক্টটি মেমোরি থেকে মুছে ফেলার ঠিক আগ মুহূর্তে, CPython ইঞ্জিন অবজেক্টের বিল্ট-ইন `aclose()` মেথডটিকে চলমান Event 
Loop-এর কাছে একটি background task হিসেবে স্বয়ংক্রিয়ভাবে পাঠিয়ে দেয়।

Step-4 (Finally Run): ইভেন্ট লুপ যখনই এই ব্যাকগ্রাউন্ড টাস্কটি প্রসেস করে, তখন জেনারেটরের পজড (paused) থাকা `yield` লাইনের ভেতরে একটি ইন্টারনাল 
`GeneratorExit` exception পুশ করা হয়। জেনারেটরটি তখন পজড অবস্থা থেকে মুক্ত হয়ে সরাসরি তার শরীরের ভেতরের `finally` ব্লকে চলে যায় এবং ক্লিনআপ 
কোডটি স্বয়ংক্রিয়ভাবে রান করে।
"""

open()