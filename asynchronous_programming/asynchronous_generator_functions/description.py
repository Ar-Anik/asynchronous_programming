"""
অ্যাসিনক্রোনাস জেনারেটর ফাংশন (Asynchronous Generator Functions)

__anext__ এবং __aiter__ সহ একটি class লিখে একটি asynchronous iterator তৈরি করা সম্ভব, তবে এর একটি সহজ উপায় রয়েছে: async def দিয়ে একটি function declare করে এর ভেতরে yield ব্যবহার করা। এটি classic Iterator pattern-কে generator function যেভাবে সহজ করে, ঠিক তার সমতুল্য।

async for ব্যবহার করে একটি asynchronous generator তৈরি করার একটি সহজ উদাহরণ দেখা যাক। Example 21-1 এ blogdom.py নামক একটি script দেখা গিয়েছিলো, যা domain name-গুলো probe (অনুসন্ধান) করতো। এখন মনে করা যাক, সেখানে define করা probe coroutine-এর আরও কিছু ব্যবহার পাওয়া গেলো এবং এটিকে domainlib.py নামক একটি নতুন module-এ রাখার সিদ্ধান্ত নেওয়া হলো। এর সাথে একটি নতুন multi_probe asynchronous generator যুক্ত করা হবে, যা domain name-এর একটি list গ্রহণ করে এবং probe করার সাথে সাথে ফলাফলগুলো yield করে।

domainlib.py-এর বাস্তবায়ন একটু পরেই দেখা হবে, তবে প্রথমে Python-এর নতুন asynchronous console-এর সাথে এটি কীভাবে ব্যবহৃত হয় তা দেখে নেওয়া যাক।

Python-এর async console নিয়ে কাজ করা
Python 3.8 থেকে, -m asyncio command-line option ব্যবহার করে interpreter run করলে একটি "async REPL" পাওয়া যায়। এটি এমন একটি Python console যা asyncio import করে, একটি চলমান event loop প্রদান করে এবং top-level prompt-এ await, async for এবং async with গ্রহণ করে (যেগুলো সাধারণত native coroutine-এর বাইরে ব্যবহার করলে syntax error দেখায়)।

domainlib.py নিয়ে পরীক্ষা করার জন্য Fluent Python code repository-এর local copy থেকে 21-async/domains/asyncio/ directory-তে গিয়ে নিচের command run করতে হবে:

Bash
$ python -m asyncio
এর ফলে নিচের মতো একটি console চালু হবে:

Plaintext
asyncio REPL 3.9.1 (v3.9.1:1e5d33e9b9, Dec 7 2020, 12:10:52)
[Clang 6.0 (clang-600.0.57)] on darwin
Use "await" directly instead of "asyncio.run()".
Type "help", "copyright", "credits" or "license" for more information.
>>> import asyncio
>>>
এখানে লক্ষ্য করার বিষয় হলো, header-এ বলা আছে coroutine এবং অন্যান্য awaitable চালানোর জন্য asyncio.run()-এর পরিবর্তে সরাসরি await ব্যবহার করা যাবে। এছাড়াও, import asyncio manually type করার প্রয়োজন হয়নি। asyncio module স্বয়ংক্রিয়ভাবে (automatic) import হয়ে যায় এবং ওই লাইনটি ব্যবহারকারীর কাছে বিষয়টি পরিষ্কার করে।

এবার domainlib.py import করে এর দুটি coroutine: probe এবং multi_probe নিয়ে কাজ করা যাক (Example 21-16)।

Example 21-16. python3 -m asyncio run করার পর domainlib.py নিয়ে পরীক্ষা


>>> await asyncio.sleep(3, 'Rise and shine!')
'Rise and shine!'
>>> from domainlib import *
>>> await probe('python.org')
Result(domain='python.org', found=True)
>>> names = 'python.org rust-lang.org golang.org no-lang.invalid'.split()
>>> async for result in multi_probe(names):
...     print(*result, sep='\t')
...
golang.org      True
no-lang.invalid False
python.org      True
rust-lang.org   True
>>>
১. Asynchronous console কীভাবে কাজ করে তা দেখার জন্য একটি সাধারণ await চেষ্টা করা হয়েছে। (Tip: asyncio.sleep() একটি ঐচ্ছিক বা optional দ্বিতীয় argument গ্রহণ করে যা await করার পর return হয়)।
২. probe coroutine-টি চালানো হয়েছে।
৩. probe-এর domainlib version একটি Result নামক named tuple return করে।
৪. Domain-এর একটি list তৈরি করা হয়েছে। .invalid top-level domain-টি testing-এর জন্য সংরক্ষিত। এ ধরনের domain-এর DNS query সবসময় DNS server থেকে একটি NXDOMAIN response পায়, যার অর্থ "সেই domain-এর কোনো অস্তিত্ব নেই।"
৫. ফলাফল প্রদর্শনের জন্য multi_probe asynchronous generator-এর ওপর async for দিয়ে iterate করা হয়েছে।
৬. লক্ষণীয় যে, multi_probe-এ domain-গুলো যে sequence-এ দেওয়া হয়েছিলো, ফলাফলগুলো সেই ক্রমানুসারে আসেনি। প্রতিটি DNS response আসার সাথে সাথেই ফলাফল প্রদর্শিত হয়েছে।

Example 21-16 থেকে বোঝা যায় যে multi_probe হলো একটি asynchronous generator, কারণ এটি async for-এর সাথে সামঞ্জস্যপূর্ণ। এবার Example 21-17 এর মাধ্যমে এই উদাহরণটির ধারাবাহিকতায় আরও কিছু পরীক্ষা করা যাক।

Example 21-17. Example 21-16 এর পর আরও কিছু পরীক্ষা

Python
>>> probe('python.org')
>>> multi_probe(names)
>>> for r in multi_probe(names):
...     print(r)
...
Traceback (most recent call last):
 ...
TypeError: 'async_generator' object is not iterable
১. একটি native coroutine call করলে একটি coroutine object পাওয়া যায়।
২. একটি asynchronous generator call করলে একটি async_generator object পাওয়া যায়।
৩. Asynchronous generator-এর সাথে সাধারণ for loop ব্যবহার করা যায় না, কারণ এগুলো __iter__-এর পরিবর্তে __aiter__ implement করে।

Asynchronous generator-গুলো async for দ্বারা পরিচালিত হয়, যা একটি block statement হতে পারে (যেমনটি Example 21-16 এ দেখা গেছে) এবং এটি asynchronous comprehension-এও ব্যবহৃত হয়, যা পরবর্তীতে আলোচনা করা হবে।

Asynchronous Generator Implement করা
এবার multi_probe asynchronous generator-সহ domainlib.py-এর code পর্যালোচনা করা যাক (Example 21-18)।

Example 21-18. domainlib.py: Domain probe করার function সমূহ

Python
import asyncio
import socket
from collections.abc import Iterable, AsyncIterator
from typing import NamedTuple, Optional

class Result(NamedTuple):
    domain: str
    found: bool

OptionalLoop = Optional[asyncio.AbstractEventLoop]

async def probe(domain: str, loop: OptionalLoop = None) -> Result:
    if loop is None:
        loop = asyncio.get_running_loop()
    try:
        await loop.getaddrinfo(domain, None)
    except socket.gaierror:
        return Result(domain, False)
    return Result(domain, True)

async def multi_probe(domains: Iterable[str]) -> AsyncIterator[Result]:
    loop = asyncio.get_running_loop()
    coros = [probe(domain, loop) for domain in domains]

    for coro in asyncio.as_completed(coros):
        result = await coro
        yield result
১. NamedTuple ব্যবহারের ফলে probe থেকে প্রাপ্ত ফলাফল পড়া এবং debug করা সহজ হয়।
২. এই type alias-টি ব্যবহার করা হয়েছে যাতে বইয়ের list-এর জন্য পরের লাইনটি অতিরিক্ত বড় হয়ে না যায়।
৩. multi_probe দ্বারা চালিত হওয়ার সময় get_running_loop-এ বারবার call করা এড়ানোর জন্য probe-এ এখন একটি ঐচ্ছিক loop argument দেওয়া হয়েছে।
৪. একটি asynchronous generator function একটি asynchronous generator object তৈরি করে, যাকে AsyncIterator[SomeType] হিসেবে annotate করা যায়।
৫. আলাদা আলাদা domain-এর জন্য probe coroutine object-গুলোর একটি list তৈরি করা হয়েছে।
৬. এখানে async for ব্যবহার করা হয়নি কারণ asyncio.as_completed হলো একটি classic generator।
৭. ফলাফল পাওয়ার জন্য coroutine object-এর ওপর await করা হয়েছে।
৮. ফলাফল yield করা হয়েছে। এই লাইনটিই মূলত multi_probe-কে একটি asynchronous generator-এ পরিণত করেছে।

Example 21-18 এর for loop-টি আরও সংক্ষেপে লেখা যেতো:

Python
        for coro in asyncio.as_completed(coros):
            yield await coro
Python এটিকে yield (await coro) হিসেবে parse করে, তাই এটি সঠিকভাবে কাজ করে। বইয়ের প্রথম asynchronous generator-এর উদাহরণে এই shortcut ব্যবহার করলে বিষয়টি বিভ্রান্তিকর হতে পারে বিবেচনা করে, এটিকে দুটি আলাদা লাইনে ভাগ করা হয়েছে।

domainlib.py ব্যবহার করে domaincheck.py-তে multi_probe asynchronous generator-এর ব্যবহার দেখানো যেতে পারে। এটি এমন একটি script যা একটি domain suffix গ্রহণ করে এবং ছোট Python keyword দিয়ে তৈরি domain-গুলো অনুসন্ধান করে।

নিচে domaincheck.py-এর একটি sample output দেওয়া হলো:

Plaintext
$ ./domaincheck.py net
FOUND            NOT FOUND
=====            =========
in.net
del.net
true.net
for.net
is.net
                 none.net
try.net
                 from.net
and.net
or.net
else.net
with.net
if.net
as.net
                 elif.net
                 pass.net
                 not.net
                 def.net
domainlib-এর কারণে domaincheck.py-এর code অত্যন্ত সহজ এবং সাবলীল হয়েছে, যা Example 21-19 এ দেখা যাচ্ছে।

Example 21-19. domaincheck.py: domainlib ব্যবহার করে domain probe করার utility

Python
#!/usr/bin/env python3
import asyncio
import sys
from keyword import kwlist
from domainlib import multi_probe

async def main(tld: str) -> None:
    tld = tld.strip('.')
    names = (kw for kw in kwlist if len(kw) <= 4)
    domains = (f'{name}.{tld}'.lower() for name in names)
    print('FOUND\t\tNOT FOUND')
    print('=====\t\t=========')
    async for domain, found in multi_probe(domains):
        indent = '' if found else '\t\t'
        print(f'{indent}{domain}')

if __name__ == '__main__':
    if len(sys.argv) == 2:
        asyncio.run(main(sys.argv[1]))
    else:
        print('Please provide a TLD.', f'Example: {sys.argv[0]} COM.BR')
১. সর্বোচ্চ ৪ অক্ষরের দৈর্ঘ্যের keyword-গুলো generate করা হয়েছে।
২. প্রদত্ত suffix-কে TLD হিসেবে ব্যবহার করে domain name generate করা হয়েছে।
৩. Tabular output-এর জন্য একটি header format করা হয়েছে।
৪. multi_probe(domains)-এর ওপর asynchronously iterate করা হয়েছে।
৫. ফলাফলটি সঠিক কলামে রাখার জন্য indent-কে শূন্য অথবা দুটি tab হিসেবে set করা হয়েছে।
৬. Command-line থেকে পাওয়া argument দিয়ে main coroutine-টি চালানো হয়েছে।

Iteration ছাড়াও generator-গুলোর আরও একটি অতিরিক্ত ব্যবহার রয়েছে: এগুলোকে context manager হিসেবে তৈরি করা যায়। এটি asynchronous generator-গুলোর ক্ষেত্রেও প্রযোজ্য।

Context Manager হিসেবে Asynchronous Generator
নিজেদের জন্য asynchronous context manager লেখা খুব সাধারণ কোনো programming কাজ নয়, তবে যদি কখনো লেখার প্রয়োজন হয়, তবে Python 3.7-এর contextlib module-এ যুক্ত হওয়া @asynccontextmanager decorator ব্যবহার করার কথা বিবেচনা করা যেতে পারে। এটি আগে পড়া @contextmanager decorator-এর মতোই কাজ করে।

Caleb Hattingh-এর লেখা Using Asyncio in Python বইয়ে @asynccontextmanager এবং loop.run_in_executor-এর সমন্বয়ে একটি চমৎকার উদাহরণ রয়েছে। Example 21-20 হলো Caleb-এর লেখা সেই code—যেখানে একটি মাত্র পরিবর্তন আনা হয়েছে এবং কিছু ব্যাখ্যামূলক অংশ যুক্ত করা হয়েছে।

Example 21-20. @asynccontextmanager এবং loop.run_in_executor ব্যবহারের উদাহরণ

Python
from contextlib import asynccontextmanager

@asynccontextmanager
async def web_page(url):
    loop = asyncio.get_running_loop()
    data = await loop.run_in_executor(None, download_webpage, url)

    yield data

    await loop.run_in_executor(None, update_stats, url)

async with web_page('google.com') as data:
    process(data)
১. Decorated function-টি অবশ্যই একটি asynchronous generator হতে হবে।
২. Caleb-এর code-এ একটি ছোট পরিবর্তন: get_event_loop-এর পরিবর্তে তুলনামূলক হালকা get_running_loop ব্যবহার করা হয়েছে।
৩. মনে করা যাক, download_webpage হলো requests library ব্যবহার করা একটি blocking function; event loop যাতে block না হয় সেজন্য এটিকে একটি আলাদা thread-এ চালানো হয়েছে।
৪. এই yield expression-এর আগের সব লাইন decorator দ্বারা তৈরি হওয়া asynchronous context manager-এর __aenter__ coroutine method-এ পরিণত হবে। নিচে async with statement-এর as clause-এর পর data variable-টিতে এই data-এর value bind হবে।
৫. yield-এর পরের লাইনগুলো __aexit__ coroutine method-এ পরিণত হবে। এখানে আরও একটি blocking call-কে thread executor-এর কাছে হস্তান্তর করা হয়েছে।
৬. async with ব্যবহার করে web_page function-টিকে call করা হয়েছে।

এটি sequential @contextmanager decorator-এর সাথে দারুণভাবে মিলে যায়। yield লাইনে error handling সহ আরও বিস্তারিত জানতে পূর্বের আলোচনাটি দেখা যেতে পারে। @asynccontextmanager-এর আরও উদাহরণের জন্য contextlib documentation পড়া যেতে পারে।

এবার native coroutine-এর সাথে তুলনা করার মাধ্যমে asynchronous generator function-এর আলোচনা সমাপ্ত করা যাক।

Asynchronous Generator বনাম Native Coroutine
একটি native coroutine এবং একটি asynchronous generator function-এর মধ্যে কিছু মূল সাদৃশ্য এবং পার্থক্য নিচে দেওয়া হলো:

উভয়কেই async def ব্যবহার করে declare করা হয়।

একটি asynchronous generator-এর body-তে সব সময়ই একটি yield expression থাকে—যা এটিকে একটি generator-এ পরিণত করে। একটি native coroutine-এর ভেতরে কখনোই yield থাকে না।

একটি native coroutine None ছাড়া অন্য কোনো value return করতে পারে। কিন্তু একটি asynchronous generator শুধুমাত্র ফাঁকা return statement ব্যবহার করতে পারে।

Native coroutine-গুলো awaitable হয়: এগুলো await expression-এর মাধ্যমে চালানো যায় অথবা create_task-এর মতো asyncio function-গুলোতে awaitable argument হিসেবে pass করা যায়। অন্যদিকে, Asynchronous generator-গুলো awaitable নয়। এগুলো মূলত asynchronous iterable, যা async for অথবা asynchronous comprehension দ্বারা পরিচালিত হয়।
"""