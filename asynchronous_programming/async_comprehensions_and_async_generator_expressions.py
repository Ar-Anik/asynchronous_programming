"""
-> Async Comprehensions এবং Async Generator Expressions
Python 3.6 থেকে শুরু করে, PEP 530—Asynchronous Comprehensions-এর মাধ্যমে comprehensions এবং generator expressions-এর syntax-এ async for এবং await-এর ব্যবহার প্রবর্তন করা হয়। PEP 530 দ্বারা define করা একমাত্র construct যা async def body-এর বাইরে ব্যবহার করা যায়, তা হলো asynchronous generator expression।

একটি asynchronous generator expression define এবং ব্যবহার করার পদ্ধতি

Example 21-18-এ দেওয়া multi_probe asynchronous generator-টি বিবেচনা করলে, এমন আরেকটি asynchronous generator লেখা সম্ভব যা শুধুমাত্র খুঁজে পাওয়া domain-গুলোর নাম return করবে। -m asyncio দিয়ে চালু করা asynchronous console ব্যবহার করে এটি কীভাবে করা যায় তা নিচে দেখানো হলো:

>>> from domainlib import multi_probe
>>> names = 'python.org rust-lang.org golang.org no-lang.invalid'.split()
>>> gen_found = (name async for name, found in multi_probe(names) if found)
>>> gen_found
<async_generator object <genexpr> at 0x10a8f9700>
>>> async for name in gen_found:
...     print(name)
...
golang.org
python.org
rust-lang.org

1. async for-এর ব্যবহার একে একটি asynchronous generator expression-এ পরিণত করে। এটি যেকোনো Python module-এর যেকোনো জায়গায় define করা যেতে পারে।
2. এই asynchronous generator expression একটি async_generator object তৈরি করে—যা হুবহু multi_probe-এর মতো একটি asynchronous generator function থেকে return হওয়া object-এর সমতুল্য।
3. এই asynchronous generator object-টি async for statement দ্বারা পরিচালিত হয়, যা শুধুমাত্র একটি async def body-এর ভেতরে অথবা এই উদাহরণে ব্যবহৃত ম্যাজিক asynchronous console-এ থাকতে পারে।

সংক্ষেপে বলা যায়: একটি asynchronous generator expression যেকোনো program-এর যেকোনো স্থানে define করা যায়, তবে এটি শুধুমাত্র একটি native coroutine অথবা asynchronous generator function-এর ভেতরেই ব্যবহার (consume) করা সম্ভব।

PEP 530 দ্বারা প্রবর্তিত বাকি construct-গুলো শুধুমাত্র native coroutines অথবা asynchronous generator function-এর ভেতরেই define এবং ব্যবহার করা যায়।

-> Asynchronous comprehensions
PEP 530-এর author Yury Selivanov নিচে দেওয়া তিনটি ছোট কোড স্নিপেটের মাধ্যমে asynchronous comprehensions-এর প্রয়োজনীয়তা সুন্দরভাবে ব্যাখ্যা করেছেন।
সবাই এই বিষয়ে একমত হতে পারে যে, নিচের কোডটি নতুন করে লেখার সক্ষমতা থাকা উচিত:

result = []
async for i in aiter():
    if i % 2:
        result.append(i)

ঠিক এইভাবে:
result = [i async for i in aiter() if i % 2]

এছাড়া, একটি native coroutine fun দেওয়া থাকলে, এভাবে লেখার সুযোগ থাকা প্রয়োজন:
result = [await fun() for fun in funcs]

list comprehension-এ await ব্যবহার করা এবং asyncio.gather ব্যবহার করা অনেকটা একই রকম। তবে gather-এর optional return_exceptions argument-এর কারণে exception handling-এর উপর আরও বেশি নিয়ন্ত্রণ পাওয়া যায়। Caleb Hattingh সবসময় return_exceptions=True (ডিফল্ট মান False থাকে) সেট করার পরামর্শ দেন। বিস্তারিত জানার জন্য asyncio.gather-এর documentation দেখা যেতে পারে।

আবার সেই ম্যাজিক asynchronous console-এ ফিরে যাওয়া যাক:

>>> names = 'python.org rust-lang.org golang.org no-lang.invalid'.split()
>>> names = sorted(names)
>>> coros = [probe(name) for name in names]
>>> await asyncio.gather(*coros)
[Result(domain='golang.org', found=True),
Result(domain='no-lang.invalid', found=False),
Result(domain='python.org', found=True),
Result(domain='rust-lang.org', found=True)]
>>> [await probe(name) for name in names]
[Result(domain='golang.org', found=True),
Result(domain='no-lang.invalid', found=False),
Result(domain='python.org', found=True),
Result(domain='rust-lang.org', found=True)]

লক্ষণীয় যে, এখানে name-এর তালিকাটি sort(ক্রমানুসারে সাজানো) করা হয়েছে এটি দেখানোর জন্য যে, উভয় ক্ষেত্রেই result-গুলো ঠিক সেই ক্রমানুসারে পাওয়া যায় যেভাবে সেগুলো submit করা হয়েছিল।
PEP 530 async for এবং await-কে list comprehensions-এর পাশাপাশি dict এবং set comprehensions-এও ব্যবহার করার অনুমতি দেয়। উদাহরণস্বরূপ, asynchronous console-এ multi_probe-এর result-গুলো সংরক্ষণ করার জন্য একটি dict comprehension নিচে দেওয়া হলো:

>>> {name: found async for name, found in multi_probe(names)}
{'golang.org': True, 'python.org': True, 'no-lang.invalid': False, 'rust-lang.org': True}

for অথবা async for clause-এর আগের expression-এ এবং if clause-এর পরের expression-এ await keyword ব্যবহার করা যায়। নিচে asynchronous console-এ একটি set comprehension দেওয়া হলো, যা শুধুমাত্র খুঁজে পাওয়া domain-গুলো সংগ্রহ করে:

>>> {name for name in names if (await probe(name)).found}
{'rust-lang.org', 'python.org', 'golang.org'}

__getattr__ operator . (ডট)-এর precedence (অগ্রাধিকার) বেশি হওয়ার কারণে এখানে await expression-এর চারপাশে অতিরিক্ত parentheses (বন্ধনী) ব্যবহার করতে হয়েছে।
পুনরায় উল্লেখ্য, এই সমস্ত comprehensions শুধুমাত্র একটি async def body-এর ভেতরে অথবা সেই বিশেষ asynchronous console-এ ব্যবহার করা যেতে পারে।

এখন async statements, async expressions এবং এদের দ্বারা তৈরি object-গুলোর একটি অত্যন্ত গুরুত্বপূর্ণ বৈশিষ্ট্য নিয়ে আলোচনা করা যাক। এই construct-গুলো প্রায়শই asyncio-এর সাথে ব্যবহার করা হয়, তবে এগুলো মূলত নির্দিষ্ট কোনো লাইব্রেরির ওপর নির্ভরশীল নয় (library independent)।
"""

"""
যখন await ছাড়া কোনো async def function call করা হয়, তখন সেই function-এর ভেতরের code রান বা execute হয় না। এর পরিবর্তে, সেটি একটি coroutine object তৈরি করে এবং তা return করে।
"""
