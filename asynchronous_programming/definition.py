"""
-> Native coroutine
async def দিয়ে define করা হয় একটি native coroutine function, classic coroutine-গুলো যেভাবে yield from ব্যবহার করে, ঠিক একইভাবে
await keyword ব্যবহার করে একটি native coroutine থেকে অন্য একটি native coroutine-এ কাজ হস্তান্তর/delegate করা যায়। async def
statement সবসময় একটি native coroutine define করে, এমনকি যদি এর ভেতরে await keyword ব্যবহার করা নাও হয়। await keyword-টি
native coroutine-এর বাইরে ব্যবহার করা যাবে না।

-> Classic coroutine
এটি এমন একটি generator function যা send(data) function-এর মাধ্যমে পাঠানো data গ্রহণ করে এবং yield keyword ব্যবহার করে সেই data
read করে। Classic coroutine-গুলো yield from ব্যবহার করে অন্য classic coroutine-এ কাজ হস্তান্তর/delegate করতে পারে। Classic
coroutine গুলোকে await দ্বারা পরিচালিত করা যায় না এবং এগুলো আর asyncio দ্বারা সমর্থিত নয়।

-> Generator-based coroutine
@types.coroutine দ্বারা Decorate করা একটি generator function—যা Python 3.5-এ চালু করা হয়েছিল। @types.coroutine ডেকোরেটরটি মূলত
একটি সাধারণ Generator-কে এমনভাবে রূপান্তরিত করে যাতে সেটি await কিওয়ার্ডের সাথে কাজ করতে পারে। এটি সাধারণত low-level library বা
framework তৈরির সময় ব্যবহৃত হয়, যেখানে async def ব্যবহার না করেও asynchronous Behavior প্রয়োজন হয়।
"""

import types
import asyncio

@types.coroutine
def generator_coro():
    print("Generator Based Coroutine is Starting....")

    result = yield
    print(f"Generator Resumed and Received Data: {result}")
    return "Work Completed"

async def main():
    print("Main Coroutine Starting....")

    # Awaiting the generator-based coro from within a native coroutine
    # This is possible specifically because of the @types.coroutine decorator
    response = await generator_coro()

    print(f"Main Corotuine Received Response : {response}")

if __name__ == '__main__':
    asyncio.run(main())

"""
সাধারণত একটি Generator function-কে await করা যায় না। কিন্তু যখন কোনো ফাংশনের উপরে @types.coroutine দেওয়া হয়, তখন Python 
internal flag `CO_ITERABLE_COROUTINE` set করে দেয়। এটি নির্দেশ করে যে, এই জেনারেটরটি এখন একটি "Awaitable" object এবং একে 
await Expression-এর ডান পাশে ব্যবহার করা যাবে।
1. যখন await generator_coro() call করা হয়, event loop বা caller তখন জেনারেটরটির ভেতর প্রবেশ করে।
2. জেনারেটরের ভেতরে যখন yield পাওয়া যায়, তখন সেটি সাময়িকভাবে স্থগিত/suspend হয়ে যায় এবং control event লুপের কাছে ফিরে যায়।
3. পরবর্তী সময়ে যখন send() method call করা হয়, তখন জেনারেটরটি ঐ yield point থেকে আবার শুরু করে।

-> Native Coroutine vs Generator-based Coroutine
* Native Coroutine: async def দিয়ে তৈরি হয়। এর ভেতরে yield ব্যবহার করলে সেটি Asynchronous Generator হয়ে যায়।
* Generator-based Coroutine: এটি একটি সাধারণ function যাতে yield থাকে, কিন্তু ডেকোরেটরের কারণে এটি await করা যায়।
"""

"""
-> Asynchronous generator
async def দিয়ে define করা একটি generator function যা এর ভেতরে yield ব্যবহার করে। এটি একটি asynchronous generator object 
return করে যা next item-টি নিয়ে আসার জন্য __anext__ নামক একটি coroutine method প্রদান করে।
"""

import asyncio

async def async_data_generator(limit):
    print("Generator Starting...")

    for i in range(1, limit + 1):
        await asyncio.sleep(1)  # for simulate i/o task
        yield f"Data {i}"

    print("Genertor End.....")

async def main():
    gen = async_data_generator(3)

    print("All Argument : ", gen.__dir__())

    item1 = await gen.__anext__()
    print("First Data : ", item1)

    item2 = await gen.__anext__()
    print("Second Data : ", item2)

    item3 = await gen.__anext__()
    print("Third Data : ", item3)


    print("Main Program Started...")
    async for item in async_data_generator(5):
        print("Get Item : ", {item})
    print("Data Processing End.....")


if __name__ == '__main__':
    asyncio.run(main())


"""
একটি Asynchronous generator-এর data processing মূলত চারটি main sequence-এ সম্পন্ন হয়। এই পুরো প্রক্রিয়াটি event loop দ্বারা নিয়ন্ত্রিত হয়।

1. Method Invocation & Request
যখন একটি async for loop চালানো হয় বা manually(__anext__ call) পরবর্তী item-টি চাওয়া হয় Asynchronous generator object থেকে, তখন event 
loop ঐ Asynchronous Generator Object-এর __anext__ মেথডটি trigger করে। যেহেতু __anext__ একটি coroutine, তাই এটি সরাসরি কোনো value 
return না করে একটি awaitable object(promise or a placeholder for future work) return করে।

2. Code Resumption & Execution
__anext__ মেথডটি call হওয়ার পর, জেনারেটরটি তার আগের save করা State থেকে পুনরায় code execute করা শুরু করে। এটি ঠিক ঐ instruction 
pointer থেকে শুরু হয় যেখানে পূর্ববর্তী iteration suspense হয়েছিল, যদি এটি প্রথমবার call করা হয়, তবে এটি ফাংশনের একদম শুরু থেকে logic check 
শুরু করে।

3. Value Yielding & Suspension
জেনারেটরের কোড চলতে চলতে যখন একটি yield statement পায়, তখন সেটি একটি value output হিসেবে প্রদান করে। এই মুহূর্তে জেনারেটরটি তার সমস্ত local 
variable এবং বর্তমান state মেমরিতে save করে রাখে এবং নিজেকে suspend বা স্থগিত করে দেয়। এই suspension অত্যন্ত গুরুত্বপূর্ণ কারণ এটি event লুপকে 
free করে দেয়, ফলে event loop অন্য কোনো task process করতে পারে।

৪. Exhaustion & Termination
যখন জেনারেটরের ভেতরে আর কোনো yield করার মতো data থাকে না বা ফাংশনের code run শেষ হয়ে যায়, তখন এটি automatic ভাবে StopAsyncIteration 
নামক exception raise করে। এটি একটি internal signal যা async for লুপকে একটি logic check প্রদান করে যে, data stream-টি শেষ হয়েছে। এর ফলে 
লুপটি কোনো error ছাড়াই সুন্দরভাবে close হয়ে যায়।
"""

"""
async for হলো Python-এর একটি বিশেষ statement, যা asynchronous iterables (যেমন: asynchronous generators) থেকে data সংগ্রহ করার জন্য 
ব্যবহৃত হয়। এটি মূলত সাধারণ for loop-এর একটি asynchronous version যা event loop-এর সাথে সামঞ্জস্য রেখে কাজ করে।

-> async for vs for
1. for loop synchronous iterable-এর উপর কাজ করে, অর্থাৎ list, tuple-এর মতো ডাটার উপর সরাসরি iteration চালায়। অন্যদিকে async for loop 
asynchronous iterable-এর উপর কাজ করে, যেখানে data ধাপে ধাপে asynchronous ভাবে পাওয়া যায়।

2. for loop iteration সম্পন্ন করতে __iter__() এবং __next__() মেথড ব্যবহার করে। কিন্তু async for loop __aiter__() এবং __anext__() মেথড 
ব্যবহার করে, যা asynchronous execution-এর জন্য উপযোগী।

3. for loop execution চলাকালে thread block করে রাখে, ফলে অন্য কোনো কাজ একসাথে করা যায় না। বিপরীতে, async for loop event loop-কে 
control ফিরিয়ে দেয়, যার ফলে একাধিক কাজ একসাথে পরিচালনা করা সম্ভব হয়।

4. for loop যেকোনো সাধারণ ফাংশনের মধ্যে ব্যবহার করা যায়। কিন্তু async for loop ব্যবহার করতে হলে অবশ্যই async def ফাংশনের ভিতরে থাকতে হয়।
"""

"""
যখন একটি async for loop চালানো হয়, তখন Python internal-ভাবে নিচের step গুলো অনুসরণ করে:

1. Object Initialization: এটি প্রথমে iterable object-এর __aiter__ method-টি call করে একটি iterator collect করে।
         
2. Requesting Next Item: এরপর এটি iterator-এর __anext__ method-টিকে call করে। যেহেতু এটি একটি asynchronous operation, তাই এটি 
প্রতিবার item সংগ্রহ করার সময় await করে।
"""
async def manual_for_loop_implement():
    iterable = async_data_generator(5)
    iterator = iterable.__aiter__()
    while True:
        try:
            item = await iterator.__anext__()    # This happens automatically
            print("Next Item : ", item)
        except StopAsyncIteration:
            break

if __name__ == '__main__':
    asyncio.run(manual_for_loop_implement())

"""
3. Suspension & Resumption: যদি পরবর্তী item প্রস্তুত না থাকে (যেমন: একটি API response-এর জন্য অপেক্ষা)(উপরের async_data_generator-এ I/O 
task বুঝানোর জন্য time.sleep() ব্যবহার করা হয়েছে), তবে এটি event loop-কে control ফেরত দিয়ে নিজেকে suspend করে। data প্রস্তুত হলে এটি পুনরায় 
active হয়ে item-টি লুপ ভেরিয়েবলে assign করে।

4. Completion Signal: যখন সব data iterate শেষ হয়ে যায়, তখন __anext__ একটি StopAsyncIteration exception raise করে, যা দেখে লুপটি 
বন্ধ হয়ে যায়।
"""

"""
যখন async for লুপ await iterator.__anext__() call করে, তখন Control-এর একটি Chain তৈরি হয়:
- Level 1: Main Code (যেখানে async for লুপটি আছে)
- Level 2: The __anext__ Method of the generator (জেনারেটরের ভেতরের কোড)
- Level 3: An internal I/O Operation or asyncio.sleep() inside the generator (একটি নির্দিষ্ট সময়ের অপেক্ষা)

ধরা যাক জেনারেটরটি, data process করার সময় 1 second বিরতি নিতে চায়। যেটা simulate করা হয়েছে async_data_generator() function-এর 
await asyncio.sleep(1) দ্বারা।

- Call: Main Code (Level 1) await generator.__anext__() call করার মাধ্যমে Control জেনারেটরকে (Level 2) দেয়।

- Inner Await: জেনারেটরের ভেতরে যখন await asyncio.sleep(1) (Level 3) লাইনটি আসে, তখন জেনারেটর নিজেও কাউকে await করছে।

- The Pause Signal: asyncio.sleep(1) যেহেতু সাথে সাথে শেষ হতে পারে না, তাই এটি একটি signal দেয়— "আমি এখন ব্যস্ত, আমাকে 1 secoond সময় দাও।"

- Bubbling Up: এই signal-টি উল্টো পথে ফিরে আসতে থাকে:
    * Level 3 থেকে সিগন্যালটি Level 2 (__anext__)-এ আসে। __anext__ নিজেকে Suspend করে দেয়।
    * Level 2 থেকে সিগন্যালটি Level 1 (async for কোড)-এ আসে। লুপটিও নিজেকে Suspend করে দেয়।
    * অবশেষে, এই সিগন্যালটি Event Loop-এর কাছে পৌঁছায়।

যখন কোডের সব Level একে একে Suspend হয়ে যায়, তখন Event Loop-এর কাছে করার মতো আর কোনো কাজ থাকে না (ঐ নির্দিষ্ট Task-টির জন্য)।
ঠিক এই মুহূর্তেই বলা হয় "Control goes back to the Event Loop"। যেহেতু Manager(Event Loop) এখন Free, সে বসে না থেকে তার Task Queue check 
করে দেখে অন্য কোনো task (যেমন: অন্য কোনো ফাংশন চালানো বা কিবোর্ড ইনপুট নেওয়া) বাকি আছে কি না। যদি থাকে, সে সেই Task গুলো করা শুরু করে। 1 Second 
পার হওয়ার পর, সে আবার জেনারেটরকে active করে এবং যেখান থেকে থেমেছিল সেখান থেকে কাজ শুরু হয়।
"""
