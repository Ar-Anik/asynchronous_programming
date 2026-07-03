"""
অ্যাসিনক্রোনাস প্রোগ্রামিংয়ে (বিশেষ করে Python asyncio-তে) Executor হলো এমন একটি মিডিয়াম বা টুল, যা কোনো ব্লকিং বা সিনক্রোনাস কাজকে (যেমন: ডিস্কে ফাইল write করা বা ভারী হিসাব-নিকাশ) মেইন ইভেন্ট লুপ (event loop) ব্লক না করে ব্যাকগ্রাউন্ডে রান করা নিশ্চিত করে।
"""

"""
অ্যাসিনক্রোনাস প্রোগ্রামিংয়ের ক্ষেত্রে Python-এর তুলনায় Node.js এর একটি বড় সুবিধা হলো এর স্ট্যান্ডার্ড লাইব্রেরি। এটি শুধুমাত্র নেটওয়ার্ক I/O নয়, বরং সব ধরনের I/O এর জন্যই অ্যাসিনক্রোনাস API প্রদান করে। Python-এ যদি সতর্কতা অবলম্বন করা না হয়, তবে ফাইল I/O অ্যাসিনক্রোনাস অ্যাপ্লিকেশনের পারফরম্যান্স মারাত্মকভাবে কমিয়ে দিতে পারে। এর কারণ হলো, মেইন থ্রেডে স্টোরেজে ডেটা রিড (read) এবং রাইট (write) করার ফলে ইভেন্ট লুপ (event loop) ব্লক হয়ে যায়।

Example 21-6-এর download_one কোরুটিনে, ডাউনলোড করা ইমেজটি ডিস্কে সেভ করতে এই লাইনটি ব্যবহার করা হয়েছিল:

Python
await asyncio.to_thread(save_flag, image, f'{cc}.gif')
পূর্বে উল্লেখ করা হয়েছে যে, asyncio.to_thread ফাংশনটি Python 3.9 ভার্সনে যুক্ত করা হয়েছিল। যদি 3.7 বা 3.8 ভার্সনে এটি সাপোর্ট করানোর প্রয়োজন হয়, তবে ওই একটি লাইনের পরিবর্তে Example 21-10-এর লাইনগুলো ব্যবহার করতে হবে।

Example 21-10. await asyncio.to_thread-এর পরিবর্তে ব্যবহারযোগ্য কোড

Python
loop = asyncio.get_running_loop()
loop.run_in_executor(None, save_flag, image, f'{cc}.gif')
১. ইভেন্ট লুপের একটি রেফারেন্স সংগ্রহ করতে হবে।
২. প্রথম আর্গুমেন্টটি হলো কোন এক্সিকিউটরটি ব্যবহার করা হবে তা নির্ধারণ করা; None পাস করার মাধ্যমে ডিফল্ট ThreadPoolExecutor নির্বাচিত হয়, যা সর্বদা asyncio ইভেন্ট লুপে বিদ্যমান থাকে।
৩. যে ফাংশনটি রান করতে হবে সেখানে পজিশনাল আর্গুমেন্ট (positional arguments) পাস করা যায়। কিন্তু যদি কিওয়ার্ড আর্গুমেন্ট (keyword arguments) পাস করার প্রয়োজন হয়, তবে run_in_executor ডকুমেন্টেশনের বর্ণনা অনুযায়ী functool.partial ব্যবহার করতে হবে।

নতুন asyncio.to_thread ফাংশনটি ব্যবহার করা অনেক সহজ এবং বেশি ফ্লেক্সিবল, কারণ এটি সরাসরি কিওয়ার্ড আর্গুমেন্টও গ্রহণ করতে পারে।

asyncio-এর নিজস্ব ইমপ্লিমেন্টেশনের ভেতরেই বেশ কয়েকটি জায়গায় run_in_executor ব্যবহার করা হয়। উদাহরণস্বরূপ, Example 21-1-এ দেখা loop.getaddrinfo(…) কোরুটিনটি socket মডিউল থেকে getaddrinfo ফাংশন কল করার মাধ্যমে ইমপ্লিমেন্ট করা হয়েছে। এটি মূলত একটি ব্লকিং ফাংশন যা ডেটা রিটার্ন করতে কয়েক সেকেন্ড সময় নিতে পারে, কারণ এটি সম্পূর্ণভাবে DNS রেজোলিউশনের ওপর নির্ভরশীল।

অ্যাসিনক্রোনাস API-গুলোর একটি সাধারণ ডিজাইন প্যাটার্ন হলো, ইমপ্লিমেন্টেশনের গভীরে থাকা ব্লকিং কলগুলোকে অভ্যন্তরীণভাবে run_in_executor ব্যবহার করে কোরুটিনের (coroutine) আবরণে র‍্যাপ (wrap) করে ফেলা। এর ফলে await দিয়ে পরিচালনা করার জন্য কোরুটিনের একটি সামঞ্জস্যপূর্ণ ইন্টারফেস প্রদান করা সম্ভব হয় এবং বাস্তবসম্মত কারণে যে থ্রেডগুলো ব্যবহার করতে হয়, সেগুলোকে আড়ালে রাখা যায়।

MongoDB-এর অ্যাসিনক্রোনাস ড্রাইভার, যার নাম Motor, সেখানে async/await সমর্থন করে এমন একটি API রয়েছে। এটি মূলত একটি থ্রেডেড কোরের (threaded core) ওপর একটি বাহ্যিক
আবরণ বা ইন্টারফেস (facade) হিসেবে কাজ করে এবং ডাটাবেস সার্ভারের সাথে যোগাযোগ স্থাপন করে। Motor ড্রাইভারের মূল কাঠামো বা ভিত্তিটি তৈরি করা হয়েছে পাইথনের প্রথাগত থ্রেড পুল (Thread Pool) দিয়ে। ডাটাবেস সার্ভারের সাথে কানেকশন তৈরি করা, ডেটা কুয়েরি করা বা ডেটা write করার মূল কাজগুলো মূলত এই থ্রেডগুলোর মাধ্যমেই সম্পন্ন হয়। সাধারণ নেটওয়ার্ক I/O-এর ক্ষেত্রে অ্যাসিনক্রোনাস পদ্ধতি দ্রুত হলেও, ডাটাবেস ড্রাইভারের মতো নির্দিষ্ট ব্যবহারের ক্ষেত্রে থ্রেড পুল অনেক বেশি পারফরম্যান্স প্রদান করে। ড্রাইভারের এই ভেতরের অংশটিই হলো থ্রেডেড কোর।
যদিও এর internal কাজগুলো থ্রেড দিয়ে হয়, কিন্তু একজন ডেভেলপার হিসেবে কোড লেখার সময় সেই থ্রেড ম্যানেজমেন্ট সরাসরি দেখতে বা হ্যান্ডেল করতে হয় না। Motor ড্রাইভারের মূল থ্রেডেড মেকানিজমের ওপরে async/await এর একটি সুন্দর এবং সামঞ্জস্যপূর্ণ আবরণ বা ইন্টারফেস ডিজাইন করা হয়েছে। এর ফলে বাইরে থেকে কোড লেখার সময় এটি একটি সাধারণ অ্যাসিনক্রোনাস ড্রাইভারের মতোই আচরণ করে। সফটওয়্যার আর্কিটেকচারে একে Facade Pattern বলা হয়, যার কাজ হলো ভেতরের জটিল ইমপ্লিমেন্টেশন লুকিয়ে রেখে বাইরে একটি সহজ ইন্টারফেস প্রদান করা।
যখন কোডে কোনো অ্যাসিনক্রোনাস কমান্ড (যেমন: await db.collection.find_one()) দেওয়া হয়, তখন এই বাহ্যিক ইন্টারফেসটি সেই কলটি গ্রহণ করে। এরপর এটি ব্যাকগ্রাউন্ডে থাকা থ্রেডেড কোরের একটি থ্রেডকে কাজটি করার জন্য দায়িত্ব দেয়। সেই থ্রেডটি ডাটাবেস সার্ভারের সাথে যোগাযোগ শেষ করে ডেটা নিয়ে আসে এবং বাহ্যিক আবরণ বা ইন্টারফেসটি আবার asyncio ইভেন্ট লুপের সাথে সামঞ্জস্য রেখে ফলাফলটি ফিরিয়ে দেয়।

Motor-এর প্রধান ডেভেলপার A. Jesse Jiryu Davis তাঁর "Response to ‘Asynchronous Python and Databases’" নামক আর্টিকেলে এর পেছনের কারণ চমৎকারভাবে ব্যাখ্যা করেছেন। চমকপ্রদ ব্যাপার হলো (Spoiler): Davis দেখতে পান যে, ডাটাবেস ড্রাইভারের মতো নির্দিষ্ট ব্যবহারের ক্ষেত্রে থ্রেড পুল (thread pool) অনেক বেশি পারফরম্যান্স দেয়। যদিও প্রচলিত ধারণা হলো, নেটওয়ার্ক I/O-এর ক্ষেত্রে থ্রেডের চেয়ে অ্যাসিনক্রোনাস পদ্ধতি সবসময় বেশি দ্রুততর হয়।

loop.run_in_executor-এ নির্দিষ্ট করে কোনো Executor পাস করার প্রধান কারণ হলো ProcessPoolExecutor ব্যবহার করা। যদি এক্সিকিউট করার ফাংশনটি CPU ইনটেনসিভ (CPU intensive) হয়, তবে এটি ভিন্ন একটি Python প্রসেসে রান করবে, যার ফলে GIL (Global Interpreter Lock)-এর বাধা এড়ানো সম্ভব হয়। যেহেতু নতুন প্রসেস শুরু করতে প্রচুর সময় ও মেমরি খরচ (high start-up cost) হয়, তাই প্রধান সুপারভাইজরে (supervisor) ProcessPoolExecutor শুরু করে নেওয়া সবচেয়ে ভালো পদ্ধতি। পরবর্তীতে যে কোরুটিনগুলোর এটি প্রয়োজন, সেগুলোর কাছে এটি পাঠিয়ে দেওয়া উচিত।

'Using Asyncio in Python (O’ Reilly)'-এর রচয়িতা Caleb Hattingh, যিনি এই বইয়ের অন্যতম টেক রিভিয়ার (tech reviewer), এক্সিকিউটর এবং asyncio সম্পর্কে নিচের সতর্কতাটি যুক্ত করার জন্য পরামর্শ দিয়েছেন।

run_in_executors সম্পর্কে কালেবের (Caleb) সতর্কতা:
run_in_executor ব্যবহার করার ফলে এমন কিছু সমস্যার সৃষ্টি হতে পারে যা ডিবাগ (debug) করা বেশ কঠিন, কারণ এর ক্যান্সেলেশন (cancellation) প্রক্রিয়া প্রত্যাশিত উপায়ে কাজ করে না। যে কোরুটিনগুলো এক্সিকিউটর ব্যবহার করে, সেগুলোকে বাতিল বা ক্যানসেল করার বিষয়টি অনেকটা লোক দেখানো (pretense of cancellation)। এর কারণ হলো, ভেতরের মূল থ্রেডের (যদি সেটি ThreadPoolExecutor হয়) নিজস্ব কোনো ক্যান্সেলেশন মেকানিজম নেই। উদাহরণস্বরূপ, run_in_executor কলের ভেতরে তৈরি হওয়া দীর্ঘ সময় ধরে চলমান (long-lived) কোনো থ্রেড, একটি asyncio প্রোগ্রামকে সঠিকভাবে বন্ধ হতে বাধা দিতে পারে। asyncio.run ফাংশনটি রিটার্ন করার পূর্বে এক্সিকিউটর সম্পূর্ণভাবে বন্ধ হওয়ার জন্য অপেক্ষা করতে থাকে। যদি এক্সিকিউটরের কাজগুলো নিজ থেকে কোনোভাবে বন্ধ না হয়, তবে এটি অনন্তকাল ধরে অপেক্ষা করতে থাকবে। এই অভিজ্ঞতার আলোকে মনে হয় যে, ফাংশনটির নাম run_in_executor_uncancellable হওয়া উচিত ছিল।
"""

# Coding Example

import asyncio
from enum import Enum
from http import HTTPStatus
from pathlib import Path
import httpx

class DownloadStatus(Enum):
    OK = 1
    NOT_FOUND = 2
    ERROR = 3

DEST_DIR = Path('delegate_task')

def save_flag(img: bytes, filename: str) -> None:
    path = DEST_DIR / filename
    with open(path, 'wb') as f:
        f.write(img)

async def get_flag(client: httpx.AsyncClient, base_url: str, cc: str) -> bytes:
    url = f'{base_url}/{cc}/{cc}.gif'.lower()
    resp = await client.get(url, timeout=3.1, follow_redirects=True)
    resp.raise_for_status()
    return resp.content


async def get_country(client: httpx.AsyncClient, base_url: str, cc: str) -> str:
    url = f'{base_url}/{cc}/metadata.json'.lower()
    resp = await client.get(url, timeout=3.1, follow_redirects=True)
    resp.raise_for_status()
    metadata = resp.json()
    return metadata['country']


async def download_one(client: httpx.AsyncClient, cc: str, base_url: str, semaphore: asyncio.Semaphore, verbose: bool) -> DownloadStatus:
    try:
        async with semaphore:
            image = await get_flag(client, base_url, cc)
        async with semaphore:
            country = await get_country(client, base_url, cc)
    except httpx.HTTPStatusError as exc:
        res = exc.response
        if res.status_code == HTTPStatus.NOT_FOUND:
            status = DownloadStatus.NOT_FOUND
            msg = f'not found: {res.url}'
        else:
            raise
    else:
        filename = country.replace(' ', '_')

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, save_flag, image, f'{filename}.gif')

        status = DownloadStatus.OK
        msg = 'OK'

    if verbose and msg:
        print(cc, msg)

    return status


async def supervisor(cc_list: list[str], base_url: str, max_concur: int) -> None:
    semaphore = asyncio.Semaphore(max_concur)

    async with httpx.AsyncClient() as client:
        to_do = [
            download_one(client, cc, base_url, semaphore, verbose=True)
            for cc in cc_list
        ]
        await asyncio.gather(*to_do)


if __name__ == '__main__':
    countries = ['bd', 'us', 'in', 'br', 'jp']
    BASE_URL = 'https://www.fluentpython.com/data/flags'

    DEST_DIR.mkdir(parents=True, exist_ok=True)

    asyncio.run(supervisor(countries, BASE_URL, max_concur=3))

