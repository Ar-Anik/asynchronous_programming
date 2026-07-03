"""
এটি @contextmanager এর মতোই কাজ করে, তবে এটি তৈরি করা হয়েছে পাইথনের asynchronous programming বা async/await ফিচারের জন্য। সাধারণত একটি
asynchronous context manager তৈরি করতে গেলে একটি class লিখে তার ভেতরে aenter এবং aexit নামের দুটি asynchronous method লিখতে হয়। কিন্তু এই
decorator ব্যবহার করলে কোনো class না লিখে, শুধুমাত্র একটি asynchronous generator function (async def এবং yield এর সমন্বয়ে গঠিত) দিয়েই
async with statement এর কাজ সম্পন্ন করা যায়।

যখন এমন কোনো resource (যেমন: asynchronous database connection, asynchronous network socket বা HTTP client session) ব্যবহার করার
প্রয়োজন হয়, তখন সঠিক সময়ে তা open বা acquire করা এবং কাজ শেষে তা close বা resource release করা নিশ্চিত করতে এই decorator ব্যবহৃত হয়।
"""

import asyncio
from contextlib import asynccontextmanager

class AsyncDatabaseConnection:
    async def connect(self):
        print("Database Connection Established Asynchronously")
        return self

    async def fetch_data(self, query):
        await asyncio.sleep(1)
        return f'Results for {query}'

    async def disconnect(self):
        print('Database Connection Closed Asynchronously.')


@asynccontextmanager
async def get_db_session():
    db = AsyncDatabaseConnection()
    conn = await db.connect()

    try:
        yield conn
    finally:
        await db.disconnect()


async def main():
    async with get_db_session() as session:
        data = await session.fetch_data("SELECT * FROM Users")
        print(f'Data Received: {data}')

asyncio.run(main())

"""
Phase 1: Initialization & Decoration (Compilation Time)

PART 1: The Asynchronous Generator Function Discovery

async def get_db_session():
    db = AsyncDatabaseConnection()
    conn = await db.connect()
    try:
        yield conn
    finally:
        ...

ফাংশনটির শুরুতে `async def` এবং ভেতরে `yield` keyword থাকার কারণে python compiler এটিকে সাধারণ function বা সাধারণ coroutine হিসেবে বিবেচনা 
করে না। এটি একটি asynchronous generator function হিসেবে মেমোরিতে registered হয়।

PART 2: @asynccontextmanager Applied

@asynccontextmanager
async def get_db_session():

Behind the Scenes, এই লাইনটি অরিজিনাল asynchronous generator ফাংশনটির উপর ডেকোরেটর প্রয়োগ করে। এটি internally নিচের কাজটি সম্পন্ন করে:
    get_db_session = asynccontextmanager(get_db_session)


PART 3: asynccontextmanager() Internal Function

def asynccontextmanager(func):
    def helper(*args, kwargs):
        return _AsyncGeneratorContextManager(func, args, kwargs)
    return helper


ডেকোরেটর ফাংশনটি অরিজিনাল ফাংশনটিকে একটি সাধারণ `helper` function দ্বারা প্রতিস্থাপন করে। `get_db_session` এখন আর সরাসরি asynchronous 
generator function নয়, এটি এখন একটি `helper` function।

PART 4: Factory Invocation
    get_db_session()

এই function call-টি execute হওয়া মানে মূলত `helper()` ফাংশনটি run হওয়া। এটি ব্যাকগ্রাউন্ডে `_AsyncGeneratorContextManager` ক্লাসের একটি object 
তৈরি করে return করে।

PART 5: The `_AsyncGeneratorContextManager` Features
পাইথনের internal `_AsyncGeneratorContextManager` ক্লাসটির ভেতরে asynchronous context manager protocol বাস্তবায়নের জন্য দুটি asynchronous 
method থাকে:
    1. `async def __aenter__(self):`
    2. `async def __aexit__(self, type, value, traceback):`


Phase 2: Runtime Execution Lifecycle

PART 6: `async with` Block Initialization

    async with get_db_session() as session:

যখন code execution `async with` লাইনে পৌঁছায়, তখন python factory object থেকে তৈরি হওয়া `_AsyncGeneratorContextManager` এর 
`__aenter__` মেথডটিকে `await` করে call করে। Internal Call like, session = await manager.aenter()


PART 7: Asynchronous Generator Activation via `__aenter__`
পাইথনের internal `__aenter__` মেথডটি সরাসরি object return করে না বরং এটি built-in `anext()` function (যা মূলত `await agen.__anext__()` 
run করে) দিয়ে asynchronous generator-টিকে প্রথমবার active করে:

async def __aenter__(self):
    return await anext(self.gen)


PART 8: Execution up to `yield` & The Yield Wait
`anext()` call হওয়ার কারণে asynchronous generator-টি তার প্রথম লাইন থেকে execute হওয়া শুরু করে। এর ফলে নিচের কোডগুলো run হয়:

db = AsyncDatabaseConnection()
conn = await db.connect()   # "Database Connection Established Asynchronously" print হয়

connection তৈরি হওয়ার পর কোডটি যখন `try` ব্লকের ভেতরের `yield conn` লাইনে পৌঁছায়, তখন asynchronous generator-টি মেমোরিতে তার সমস্ত local 
variable এবং state সহ সাময়িকভাবে pause হয়ে দাঁড়িয়ে থাকে।


PART 9: Target Variable Binding
`yield conn` লাইনে জেনারেটরটি pause হওয়ার মুহূর্তে যে `conn` অবজেক্টটি release হয়েছিল, তা `__aenter__` মেথডের output হিসেবে ফিরে আসে। পাইথন 
তখন সেই অবজেক্টটিকে `as session` অংশের `session` ভেরিয়েবলের সাথে bind করে দেয়। `__aenter__` এর কাজ এখানে শেষ হয়।

PART 10: Asynchronous Block Body Executes
এখন `async with` ব্লকের ভেতরের main code execute হওয়া শুরু করে:

data = await session.fetch_data("SELECT * FROM Users")
print(f'Data Received: {data}')

যখন `await session.fetch_data(...)` run হয়, তখন তার ভেতরের `await asyncio.sleep(1)` লাইনটি trigger হয়। এই wait করার সময়ে current task-টি 
pause হয় এবং event loop অন্য কোনো ready task থাকলে তা execute করার সুযোগ পায়। এই পুরো সময় জুড়ে generator ফাংশনটি কিন্তু ঐ `yield` লাইনেই 
paused অবস্থায় স্থির থাকে।

PART 11: `async with` Block Exit
ব্লকের ভেতরের শেষ লাইন execute হওয়া শেষ হওয়া মাত্রই (অথবা ব্লকের ভেতরে কোনো un-handled exception ঘটলেও) পাইথন `async with` ব্লক থেকে বের হওয়ার 
জন্য Internally `__aexit__` মেথডটিকে `await` করে call করে। Internal Call: await manager.__aexit__(None, None, None)


PART 12: Generator Resumption inside `__aexit__`
যদি ব্লকের ভেতরে কোনো error না হয়ে থাকে, তবে `__aexit__` মেথডটি পুনরায় Internally `anext()` call করে ঐ `yield` লাইনে pause হয়ে থাকা 
asynchronous generator-টিকে আবার active করে:
  
async def __aexit__(self, type, value, traceback):
  if type is None:
      try:
          await anext(self.gen)
      except StopAsyncIteration:
          return True


PART 13: Finally Block Execution & Cleanup
`anext()` কলের কারণে জেনারেটরটি তার `yield` লাইনের ঠিক পরের অংশ অর্থাৎ `finally` ব্লকে প্রবেশ করে এবং closing কোডটি execute করে:

finally:
    await db.disconnect()   # "Database Connection Closed Asynchronously." print হয়



PART 14: The `StopAsyncIteration` Termination
`finally` ব্লকের কাজ শেষ হওয়া মাত্রই asynchronous generator ফাংশনটির lifetime সম্পূর্ণ শেষ হয়ে যায় এবং পাইথন একটি internal `StopAsyncIteration` 
exception raise করে।
"""
