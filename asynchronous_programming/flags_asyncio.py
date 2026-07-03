import time
import asyncio
from pathlib import Path
from typing import Callable
from httpx import AsyncClient

POP20_CC = 'CN IN US ID BR PK NG BD RU JP MX PH VN ET EG DE IR TR CD FR'.split()

BASE_URL = 'https://www.fluentpython.com/data/flags'
DEST_DIR = Path('asynchronously_downloaded_flag')

def save_flag(img: bytes, filename:str) -> None:
    (DEST_DIR/filename).write_bytes(img)


async def get_flag(client: AsyncClient, cc: str) -> bytes:
    url = f'{BASE_URL}/{cc}/{cc}.gif'.lower()
    resp = await client.get(url, timeout=6.1, follow_redirects=True)
    return resp.read()


async def download_one(client: AsyncClient, cc: str):
    image = await get_flag(client, cc)
    save_flag(image, f'{cc}.gif')
    print(cc, end=' ', flush=True)
    return cc


"""
-> Asynchronous I/O এবং AsyncClient
নেটওয়ার্কের মাধ্যমে কোনো web server থেকে file download করা এক ধরণের I/O-bound (Input/Output) কাজ। প্রথাগত coding পদ্ধতিতে একটি নেটওয়ার্ক 
request পাঠানোর পর, server থেকে চূড়ান্ত response না আসা পর্যন্ত সম্পূর্ণ program next লাইন Execute করা বন্ধ করে দেয়। একে Blocking code বলা হয়।

httpx.AsyncClient হলো একটি non-blocking HTTP client। এটি পাইথনের asyncio ecosystem এর সাথে সামঞ্জস্যপূর্ণভাবে কাজ করার জন্য তৈরি। এর প্রধান 
কাজ হলো, যখন একটি network request পাঠানো হবে, তখন response এর জন্য অলস বসে না থেকে system এর main control event loop এর কাছে ফিরিয়ে 
দেওয়া, যাতে একই সময়ে অন্যান্য task চালানো যায়।

Q : কেন requests ব্যবহার না করে AsyncClient ব্যবহার করা হয়েছে?
-> যদি এই কোডে প্রথাগত requests.get() বা requests.Session() ব্যবহার করা হতো, তবে নিচের সমস্যাগুলো দেখা দিত:
- Sequential Execution : ২০টি দেশের flag download করার জন্য কোডটি প্রথম দেশের request পাঠিয়ে সম্পূর্ণ pause হয়ে বসে থাকত। প্রথমটির download শেষ 
হলে তবেই দ্বিতীয়টির কাজ শুরু হতো। এতে প্রচুর সময় নষ্ট হতো।

- Thread Limitations: requests লাইব্রেরিকে সমান্তরালভাবে চালাতে গেলে Multi-threading ব্যবহার করতে হয়, যা অধিক মেমোরি ও Processor resources গ্রহণ করে।

- Async incompatibility: সাধারণ requests লাইব্রেরি পাইথনের async এবং await keyword সমর্থন করে না। ফলে এটি asyncio.gather এর ভেতরে চললেও 
সম্পূর্ণ system কে block করে রাখত।

httpx.AsyncClient ব্যবহারের ফলে একটি মাত্র thread ব্যবহার করেই ২০টি request প্রায় 1 millisecond সময়ের মধ্যে একসাথে পাঠিয়ে দেওয়া সম্ভব হয়।
"""

async def supervisor(cc_list: list[str]) -> int:
    async with AsyncClient() as client:
        to_do = [download_one(client, cc) for cc in sorted(cc_list)]
        res = await asyncio.gather(*to_do)

    return len(res)

def download_many(cc_list: list[str]) -> int:
    return asyncio.run(supervisor(cc_list))

def main(downloader: Callable[[list[str]], int]) -> None:
    DEST_DIR.mkdir(exist_ok=True)
    t0 = time.perf_counter()
    count = downloader(POP20_CC)
    elapsed = time.perf_counter() - t0
    print(f'\n{count} downloads in {elapsed:.2f}s')


if __name__ == '__main__':
    main(download_many)

"""
Step-1: Central Event Loop চালু করা

def download_many(cc_list: list[str]) -> int:
    return asyncio.run(supervisor(cc_list))

- asyncio.run() এই অ্যাপ্লিকেশনের জন্য একটি central event loop তৈরি এবং সক্রিয় করে।
- এটি supervisor নামক প্রধান coroutine ফাংশনটিকে execute করার দায়িত্ব নেয়।

Step-2: Connection Pool এবং Task List তৈরি

async def supervisor(cc_list: list[str]) -> int:
    async with AsyncClient() as client:
        to_do = [download_one(client, cc) for cc in sorted(cc_list)]

- async with AsyncClient() as client: এখানে একটি নির্দিষ্ট client object তৈরি করা হচ্ছে। এর ভেতরে একটি internal connection pool থাকে। এই 
pool থাকার কারণে 20 টি দেশের ডাউনলোডের জন্য আলাদা আলাদা 20 বার নেটওয়ার্ক handshake করতে হয় না; একই Connection বারবার ব্যবহার করা যায়।

- async with একটি Asynchronous Context Manager হিসেবে কাজ করে। এর কাজ হলো ব্লকের ভেতরের কাজ শেষ হওয়া মাত্রই Open থাকা সমস্ত নেটওয়ার্ক socket 
automatic ভাবে বন্ধ করে দেওয়া, যা memory leak হওয়া রোধ করে।

- to_do = [...] লাইনটি একটি list comprehension। এটি প্রতিটি দেশের জন্য download_one ফাংশনের একটি করে coroutine object তৈরি করে একটি 
তালিকায় জমা রাখে। মনে রাখা প্রয়োজন, এই লাইনে কোনো নেটওয়ার্ক call বা download শুরু হয় না, এটি কেবল একটি Task List প্রস্তুত করে।

Step-3: Concurrent Execution

res = await asyncio.gather(*to_do)

- এটি এই কোডের সবচেয়ে গুরুত্বপূর্ণ command। asyncio.gather ফাংশনটি প্রস্তুত করা 20 টি task কে একসাথে event loop-এ নিবন্ধিত করে।
- এখানে থাকা await keyword টি event loop কে নির্দেশ দেয়, "এই তালিকায় থাকা সমস্ত Task সমান্তরালভাবে চালানো শুরু করো এবং সবগুলোর ফলাফল return 
না আসা পর্যন্ত এই লাইনে অপেক্ষা করো।"

Step-4: Non-Blocking Network Operation

async def get_flag(client: AsyncClient, cc: str) -> bytes:
    url = f'{BASE_URL}/{cc}/{cc}.gif'.lower()
    resp = await client.get(url, timeout=6.1, follow_redirects=True)
    return resp.read()

- যখন কোডটি await client.get(...) লাইনে পৌঁছায়, তখন AsyncClient OS লেভেলে একটি non-blocking request পাঠায়।
- await থাকার কারণে এই নির্দিষ্ট দেশের জন্য চলা coroutine টি সাময়িকভাবে pause হয়ে যায়। event loop তখন অলস বসে না থেকে অবিলম্বে তালিকায় থাকা 
পরবর্তী দেশের task টি চালু করে দেয়।
- ব্যাকগ্রাউন্ডে OS যখনই কোনো দেশের response সম্পূর্ণ ready পায়, সে event loop কে সংকেত পাঠায়। event loop তখন pause থাকা সেই কাজটি পুনরায় resume 
করে এবং save_flag ফাংশনের মাধ্যমে স্থানীয় hard disk বা storage এ ডাটা write করে দেয়।
"""
