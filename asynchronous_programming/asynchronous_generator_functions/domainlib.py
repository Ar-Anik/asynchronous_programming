import asyncio
import socket
from collections.abc import Iterable, AsyncIterator
from typing import NamedTuple, Optional

class Result(NamedTuple):
    domain: str
    found: bool

"""
Q : Optional কী?
Python-এর typing module-এ Optional হলো একটি Type Hint, যা বোঝাতে ব্যবহৃত হয় যে, কোনো একটি variable বা argument-এর মান একটি নির্দিষ্ট type-এর হতে পারে, অথবা সেটি None হতে পারে।
সহজ কথায়, Optional[X] এর মানে হলো মানটি হয় X type-এর হবে, নতুবা None হবে। এটি মূলত Union[X, None] লেখার একটি সুন্দর ও সংক্ষিপ্ত উপায়। উদাহরণস্বরূপ, যদি লেখা হয় Optional[int], তবে এর মানে হলো মানটি একটি integer হতে পারে অথবা None হতে পারে।
"""

OptionalLoop = Optional[asyncio.AbstractEventLoop]

"""
1. Type Alias তৈরি করে কোড ছোট ও পরিষ্কার রাখা:
asyncio.AbstractEventLoop নামটি বেশ বড়। probe function-এর parameter-এ Optional[asyncio.AbstractEventLoop] পুরোটা লিখলে লাইনের দৈর্ঘ্য অনেক বড় হয়ে যেতো (বিশেষ করে বইয়ের পৃষ্ঠায় বা স্ক্রিনে কোড দেখানোর সময় অতিরিক্ত দীর্ঘ লাইন পড়া কষ্টকর হয়)। তাই পুরো জিনিসটিকে OptionalLoop নামের একটি সংক্ষিপ্ত নামে (Type Alias) রাখা হয়েছে। এতে কোডের রিডেবিলিটি (readability) বাড়ে।

2. Function-এর Argument-এর ধরন (Type) নির্দিষ্ট করা:
domainlib.py-এর probe function-টি লক্ষ্য করলে দেখা যাবে, এর parameter-এ লেখা আছে loop: OptionalLoop = None।

এর মাধ্যমে দুটি বিষয় নিশ্চিত করা হয়েছে:
- probe function-কে call করার সময় loop parameter-টি পাঠানো সম্পূর্ণ ঐচ্ছিক।
- যদি কোনো loop পাঠানো হয়, তবে সেটি অবশ্যই একটি চলমান asyncio.AbstractEventLoop হতে হবে।
- আর যদি বাইরে থেকে কোনো loop পাঠানো না হয়, তবে এটি default মান হিসেবে None গ্রহণ করবে। পরবর্তীতে function-টির ভেতরের লজিক (if loop is None:) নিজে থেকেই একটি চলমান event loop খুঁজে নেবে।
"""

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

