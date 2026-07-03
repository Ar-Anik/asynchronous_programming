"""
asyncio.as_completed এবং Thread-এর ব্যবহার
Example 21-3-এ, একাধিক coroutines-কে asyncio.gather-এর কাছে পাঠানো হয়েছিল, যা coroutines জমা দেওয়ার sequence অনুযায়ী একটি লিস্ট আকারে ফলাফল রিটার্ন করে। এর অর্থ হলো, সমস্ত awaitables সম্পন্ন না হওয়া পর্যন্ত asyncio.gather কোনো ফলাফল রিটার্ন করতে পারে না। কিন্তু কোনো অ্যাপ্লিকেশনে লাইভ প্রোগ্রেস বার আপডেট করতে হলে প্রতিটি টাস্ক শেষ হওয়ার সাথে সাথে তার আপডেট পাওয়া আবশ্যক।

সৌভাগ্যবশত, থ্রেড পুলের উদাহরণে প্রোগ্রেস বারের সাথে যে as_completed জেনারেটর ফাংশন ব্যবহার করা হয়েছিল (Example 20-16), asyncio-তেও তার একটি সমমানের ফাংশন রয়েছে। Example 21-6-এ flags2_asyncio.py স্ক্রিপ্টের উপরের অংশ দেখানো হয়েছে যেখানে get_flag এবং download_one coroutines define করা হয়েছে। Example 21-7-এ স্ক্রিপ্টের বাকি অংশ supervisor এবং download_many সহ তালিকাভুক্ত করা হয়েছে। এরর হ্যান্ডলিংয়ের (error handling) কারণে এই স্ক্রিপ্টটি flags_asyncio.py-এর চেয়ে দীর্ঘ।

Example 21-6. flags2_asyncio.py: স্ক্রিপ্টের উপরের অংশ; বাকি কোড রয়েছে Example 21-7 এ
"""
import sys
import time
import string
import argparse
import asyncio
from http import HTTPStatus
from pathlib import Path
import httpx
import tqdm  # type: ignore
from enum import Enum
from collections import Counter


SERVERS = {
    'REMOTE': 'https://www.fluentpython.com/data/flags',
    'LOCAL':  'http://localhost:8000/flags',
    'DELAY':  'http://localhost:8001/flags',
    'ERROR':  'http://localhost:8002/flags',
}
DEFAULT_SERVER = 'REMOTE'

# low concurrency default to avoid errors from remote site,
# such as 503 - Service Temporarily Unavailable
DEFAULT_CONCUR_REQ = 5
MAX_CONCUR_REQ = 1000

COUNTRY_CODES_FILE = Path('country_codes.txt')

DownloadStatus = Enum('DownloadStatus', 'OK NOT_FOUND ERROR')

POP20_CC = ('AD AE AF AG AL AM AO AR AT AU AZ BA BB BD BE BF BG BH BI BJ BN BO BR BS BT BW BY BZ CA CD '
            'CF CG CH CI CL CM CN CO CR CU CV CY CZ DE DJ DK DM DZ EC EE EG ER ES ET FI FJ FM FR GA GB '
            'GD GE GH GM GN GQ GR GT GW GY HN HR HT HU ID IE IL IN IQ IR IS IT JM JO JP KE KG KH KI KM '
            'KN KP KR KW KZ LA LB LC LI LK LR LS LT LU LV LY MA MC MD ME MG MH MK ML MM MN MR MT MU MV '
            'MW MX MY MZ NA NE NG NI NL NO NP NR NZ OM PA PE PG PH PK PL PT PW PY QA RO RS RU RW SA SB '
            'SC SD SE SG SI SK SL SM SN SO SR SS ST SV SY SZ TD TG TH TJ TL TM TN TO TR TT TV TW TZ UA '
            'UG US UY UZ VA VC VE VN VU WS YE ZA ZM ZW').split()

DEST_DIR = Path('asynchronously_downloaded_flag')


def save_flag(img: bytes, filename:str) -> None:
    (DEST_DIR/filename).write_bytes(img)


async def get_flag(client: httpx.AsyncClient, base_url: str, cc: str) -> bytes:
    url = f'{base_url}/{cc}/{cc}.gif'.lower()
    resp = await client.get(url, timeout=3.1, follow_redirects=True)
    resp.raise_for_status()
    return resp.content


async def download_one(client: httpx.AsyncClient, cc: str, base_url: str, semaphore: asyncio.Semaphore, verbose: bool) -> DownloadStatus:
    try:
        async with semaphore:
            image = await get_flag(client, base_url, cc)
    except httpx.HTTPStatusError as exc:
        res = exc.response
        if res.status_code == HTTPStatus.NOT_FOUND:
            status = DownloadStatus.NOT_FOUND
            msg = f'not found: {res.url}'
        else:
            raise
    else:
        await asyncio.to_thread(save_flag, image, f'{cc}.gif')
        status = DownloadStatus.OK
        msg = 'OK'

    if verbose and msg:
        print(cc, msg)

    return status


def expand_cc_args(every_cc: bool, all_cc: bool, cc_args: list[str], limit: int) -> list[str]:
    codes: set[str] = set()
    A_Z = string.ascii_uppercase
    if every_cc:
        codes.update(a+b for a in A_Z for b in A_Z)
    elif all_cc:
        text = COUNTRY_CODES_FILE.read_text()
        codes.update(text.split())
    else:
        for cc in (c.upper() for c in cc_args):
            if len(cc) == 1 and cc in A_Z:
                codes.update(cc + c for c in A_Z)
            elif len(cc) == 2 and all(c in A_Z for c in cc):
                codes.add(cc)
            else:
                raise ValueError('*** Usage error: each CC argument must be A to Z or AA to ZZ.')
    return sorted(codes)[:limit]


def process_args(default_concur_req):
    server_options = ', '.join(sorted(SERVERS))
    parser = argparse.ArgumentParser(description='Download flags for country codes. ' 'Default: top 20 countries by population.')
    parser.add_argument('cc', metavar='CC', nargs='*', help='country code or 1st letter (eg. B for BA...BZ)')
    parser.add_argument('-a', '--all', action='store_true', help='get all available flags (AD to ZW)')
    parser.add_argument('-e', '--every', action='store_true', help='get flags for every possible code (AA...ZZ)')
    parser.add_argument('-l', '--limit', metavar='N', type=int, help='limit to N first codes', default=sys.maxsize)
    parser.add_argument('-m', '--max_req', metavar='CONCURRENT', type=int, default=default_concur_req, help=f'maximum concurrent requests (default={default_concur_req})')
    parser.add_argument('-s', '--server', metavar='LABEL', default=DEFAULT_SERVER, help=f'Server to hit; one of {server_options} (default={DEFAULT_SERVER})')
    parser.add_argument('-v', '--verbose', action='store_true', help='output detailed progress info')
    args = parser.parse_args()
    if args.max_req < 1:
        print('*** Usage error: --max_req CONCURRENT must be >= 1')
        parser.print_usage()
        sys.exit(2)  # command line usage error
    if args.limit < 1:
        print('*** Usage error: --limit N must be >= 1')
        parser.print_usage()
        sys.exit(2)  # command line usage error
    args.server = args.server.upper()
    if args.server not in SERVERS:
        print(f'*** Usage error: --server LABEL must be one of {server_options}')
        parser.print_usage()
        sys.exit(2)  # command line usage error
    try:
        cc_list = expand_cc_args(args.every, args.all, args.cc, args.limit)
    except ValueError as exc:
        print(exc.args[0])
        parser.print_usage()
        sys.exit(2)  # command line usage error

    if not cc_list:
        cc_list = sorted(POP20_CC)[:args.limit]
    return args, cc_list


def initial_report(cc_list: list[str], actual_req: int, server_label: str) -> None:
    if len(cc_list) <= 10:
        cc_msg = ', '.join(cc_list)
    else:
        cc_msg = f'from {cc_list[0]} to {cc_list[-1]}'
    print(f'{server_label} site: {SERVERS[server_label]}')
    plural = 's' if len(cc_list) != 1 else ''
    print(f'Searching for {len(cc_list)} flag{plural}: {cc_msg}')
    if actual_req == 1:
        print('1 connection will be used.')
    else:
        print(f'{actual_req} concurrent connections will be used.')


def final_report(cc_list: list[str], counter: Counter[DownloadStatus], start_time: float) -> None:
    elapsed = time.perf_counter() - start_time
    print('-' * 20)
    plural = 's' if counter[DownloadStatus.OK] != 1 else ''
    print(f'{counter[DownloadStatus.OK]:3} flag{plural} downloaded.')
    if counter[DownloadStatus.NOT_FOUND]:
        print(f'{counter[DownloadStatus.NOT_FOUND]:3} not found.')
    if counter[DownloadStatus.ERROR]:
        plural = 's' if counter[DownloadStatus.ERROR] != 1 else ''
        print(f'{counter[DownloadStatus.ERROR]:3} error{plural}.')
    print(f'Elapsed time: {elapsed:.2f}s')


def main(download_many, default_concur_req, max_concur_req):
    args, cc_list = process_args(default_concur_req)
    actual_req = min(args.max_req, max_concur_req, len(cc_list))
    initial_report(cc_list, actual_req, args.server)
    base_url = SERVERS[args.server]
    DEST_DIR.mkdir(exist_ok=True)

    t0 = time.perf_counter()
    counter = download_many(cc_list, base_url, args.verbose, actual_req)
    final_report(cc_list, counter, t0)
"""
কোড বিশ্লেষণ (Example 21-6)
get_flag ফাংশনটি Example 20-14-এর সিক্যুয়েন্সিয়াল সংস্করণের অত্যন্ত কাছাকাছি। প্রথম পার্থক্য: এর জন্য client প্যারামিটার প্রয়োজন।

দ্বিতীয় এবং তৃতীয় পার্থক্য: .get হলো একটি AsyncClient মেথড এবং এটি একটি coroutine, তাই একে await করা প্রয়োজন।

Semaphore-কে একটি asynchronous context manager হিসেবে ব্যবহার করা হয়েছে যেন সম্পূর্ণ প্রোগ্রামটি ব্লক না হয়; শুধুমাত্র এই coroutine-টির execution সাময়িকভাবে স্থগিত হয় যখন semaphore কাউন্টার শূন্য থাকে। "Python’s Semaphores" অংশে এই বিষয়ে বিস্তারিত রয়েছে।

এরর হ্যান্ডলিংয়ের (error handling) logic check এখানে Example 20-14-এর download_one ফাংশনের মতোই রাখা হয়েছে।

ইমেজ ফাইল ডিস্কে সংরক্ষণ বা write করা একটি আইও (I/O) অপারেশন। ইভেন্ট লুপ (event loop) ব্লক করা এড়াতে, একটি আলাদা থ্রেডের মধ্যে save_flag ফাংশনটি execute করা হয়েছে।

asyncio-তে সমস্ত নেটওয়ার্ক I/O অপারেশনের জন্য coroutines ব্যবহার করা হলেও লোকাল ফাইল আইও (File I/O)-এর জন্য তা করা হয় না। ফাইল আইও অপারেশনগুলো প্রকৃতিগতভাবে "blocking"—কারণ ডিস্কে ফাইল রিড বা write করতে RAM-এর তুলনায় হাজার গুণ বেশি সময় লাগে। Network-Attached Storage (NAS) ব্যবহারের ক্ষেত্রে এর অন্তরালে নেটওয়ার্ক I/O-ও জড়িত থাকতে পারে।

Python 3.9 থেকে প্রবর্তিত asyncio.to_thread coroutine-টি ফাইল I/O-এর কাজকে asyncio দ্বারা সরবরাহকৃত একটি থ্রেড পুলে অর্পণ করা সহজ করে তোলে। যদি Python 3.7 বা 3.8 সংস্করণ সাপোর্ট করার প্রয়োজন হয়, তবে থ্রেড পুলে টাস্ক অর্পণের জন্য executors ব্যবহার করে অতিরিক্ত কিছু লাইন যুক্ত করার নিয়ম “Delegating Tasks to Executors” অংশে দেখানো হয়েছে।

Python-এর Semaphores
কম্পিউটার বিজ্ঞানী Edsger W. Dijkstra ১৯৬০-এর দশকের শুরুতে semaphore আবিষ্কার করেন। এটি একটি অত্যন্ত ফ্লেক্সিবল ধারণা, যার ওপর ভিত্তি করে লক (locks) এবং ব্যারিয়ারের (barriers) মতো অন্যান্য সিঙ্ক্রোনাইজেশন object তৈরি করা সম্ভব। পাইথনের স্ট্যান্ডার্ড লাইব্রেরিতে তিনটি Semaphore class রয়েছে: একটি threading-এ, একটি multiprocessing-এ এবং তৃতীয়টি asyncio-তে। এখানে শেষোক্তটি আলোচনা করা হচ্ছে।

একটি asyncio.Semaphore-এর একটি internal counter থাকে যা প্রতিবার .acquire() coroutine মেথড await করার সময় এক হ্রাস পায় এবং .release() মেথড কল করার সময় এক বৃদ্ধি পায়। .release() কোনো coroutine নয়, তাই এটি কখনোই ব্লক করে না। Semaphore object তৈরি বা instantiate করার সময় কাউন্টারের প্রাথমিক মান নির্ধারণ করা হয়:


semaphore = asyncio.Semaphore(concur_req)
কাউন্টার শূন্যের চেয়ে বেশি থাকলে .acquire() কোনো বিলম্ব ছাড়াই কাজ করে। কিন্তু কাউন্টার শূন্য হলে, অন্য কোনো coroutine একই semaphore-এর ওপর .release() কল করে কাউন্টার বৃদ্ধি না করা পর্যন্ত .acquire() আহ্বানকারী coroutine-এর execution স্থগিত বা suspend রাখে।

এই মেথডগুলো সরাসরি ব্যবহারের চেয়ে semaphore-কে একটি asynchronous context manager হিসেবে ব্যবহার করা নিরাপদ, যেমনটি Example 21-6 এর download_one ফাংশনে করা হয়েছে:

async with semaphore:
    image = await get_flag(client, base_url, cc)
এখানে Semaphore.__aenter__ coroutine মেথডটি .acquire()-এর জন্য await করে এবং __aexit__ মেথডটি .release() কল করে। এই কোড স্নীপেটটি নিশ্চিত করে যেন কোনো নির্দিষ্ট সময়ে get_flag coroutine-এর concur_req সংখ্যার বেশি ইনস্ট্যান্স সক্রিয় না থাকে।

স্ট্যান্ড্যান্ড লাইব্রেরির প্রতিটি Semaphore class-এর একটি BoundedSemaphore সাবক্লাস রয়েছে, যা একটি অতিরিক্ত শর্ত আরোপ করে: যখন .acquire() অপারেশনের চেয়ে বেশি .release() অপারেশন করা হয়, তখন internal counterটি কখনো তার প্রাথমিক মানের চেয়ে বড় হতে পারে না।

Semaphore-এর মাধ্যমে Request থ্রটলিং (Throttling)
সার্ভারে একসাথে অতিরিক্ত concurrent request পাঠানো প্রতিরোধ করতে নেটওয়ার্ক ক্লায়েন্টগুলোকে থ্রটল (throttled) বা সীমাবদ্ধ করা আবশ্যক।

Semaphore হলো লকের চেয়ে অনেক বেশি ফ্লেক্সিবল একটি সিঙ্ক্রোনাইজেশন প্রিমিটিভ। একটি কনফিগারযোগ্য সর্বোচ্চ সংখ্যার ওপর ভিত্তি করে একাধিক coroutine একটি semaphore ধারণ করতে পারে। এটি সক্রিয় concurrent coroutine-এর সংখ্যা থ্রটল করার জন্য আদর্শ।

flags2_threadpool.py (Example 20-16)-এ, থ্রটলিংয়ের কাজটি করা হয়েছিল download_many ফাংশনে ThreadPoolExecutor-এর max_workers আর্গুমেন্টটি concur_req হিসেবে সেট করে। অন্যদিকে, flags2_asyncio.py-তে একটি asyncio.Semaphore তৈরি করা হয় supervisor ফাংশনের মাধ্যমে (যা Example 21-7-এ দেখানো হয়েছে) এবং তা download_one ফাংশনে semaphore আর্গুমেন্ট হিসেবে পাস করা হয়।

Example 21-7. flags2_asyncio.py: স্ক্রিপ্টের বাকি অংশ
"""
async def supervisor(cc_list: list[str], base_url: str, verbose: bool, concur_req: int) -> Counter[DownloadStatus]:
    counter: Counter[DownloadStatus] = Counter()
    semaphore = asyncio.Semaphore(concur_req)

    async with httpx.AsyncClient() as client:
        to_do = [download_one(client, cc, base_url, semaphore, verbose) for cc in sorted(cc_list)]

        to_do_iter = asyncio.as_completed(to_do)

        if not verbose:
            to_do_iter = tqdm.tqdm(to_do_iter, total=len(cc_list))

        error: httpx.HTTPError | None = None

        for coro in to_do_iter:
            try:
                status = await coro
            except httpx.HTTPStatusError as exc:
                error_msg = 'HTTP error {resp.status_code} - {resp.reason_phrase}'
                error_msg = error_msg.format(resp=exc.response)
                error = exc
            except httpx.RequestError as exc:
                error_msg = f'{exc} {type(exc)}'.strip()
                error = exc
            except KeyboardInterrupt:
                break

            if error:
                status = DownloadStatus.ERROR

                if verbose:
                    url = str(error.request.url)
                    cc = Path(url).stem.upper()
                    print(f'{cc} error: {error_msg}')
            counter[status] += 1

    return counter

def download_many(cc_list: list[str], base_url: str, verbose: bool, concur_req: int) -> Counter[DownloadStatus]:
    coro = supervisor(cc_list, base_url, verbose, concur_req)
    counts = asyncio.run(coro)

    return counts

if __name__ == '__main__':
    main(download_many, DEFAULT_CONCUR_REQ, MAX_CONCUR_REQ)
"""
কোড বিশ্লেষণ (Example 21-7)
supervisor ফাংশনটি download_many-এর মতোই একই আর্গুমেন্ট গ্রহণ করে, কিন্তু এটি একটি coroutine হওয়ায় একে main থেকে সরাসরি আহ্বান বা execute করা যায় না।

একটি asyncio.Semaphore তৈরি করা হয়েছে যা এই semaphore ব্যবহারকারী coroutine-গুলোর মধ্যে concur_req-এর বেশি সংখ্যক coroutine-কে একসাথে সক্রিয় থাকতে দেয় না। কমান্ড-লাইন অপশন এবং কনস্ট্যান্টের ওপর ভিত্তি করে main ফাংশন এই concur_req-এর মান গণনা করে।

download_one coroutine-এর প্রতিটি কলের জন্য একটি করে coroutine object-এর লিস্ট তৈরি করা হয়েছে।

একটি ইটারেটর নেওয়া হয়েছে যা coroutine objects সম্পন্ন হওয়ার সাথে সাথে তা রিটার্ন করবে। এই as_completed কলটি সরাসরি নিচের for লুপে রাখা হয়নি কারণ ব্যবহারকারীর পছন্দ অনুযায়ী এটিকে প্রোগ্রেস বারের জন্য tqdm ইটারেটর দিয়ে wrap করার প্রয়োজন হতে পারে।

প্রোগ্রেস দেখানোর জন্য as_completed ইটারেটরটিকে tqdm জেনারেটর ফাংশন দিয়ে wrap করা হয়েছে।

error ভেরিয়েবলটি None দিয়ে ইনিশিয়ালাইজ করা হয়েছে; কোনো এক্সেপশন রেইজ হলে try/except স্টেটমেন্টের বাইরেও এক্সেপশনটি ধরে রাখার জন্য এই ভেরিয়েবলটি ব্যবহার করা হবে।

সম্পন্ন হওয়া coroutine objects-এর ওপর লুপ চালানো হয়েছে; এই লুপটি Example 20-16 এর download_many ফাংশনের লুপের মতোই।

রেজাল্ট বা ফলাফল পাওয়ার জন্য coroutine-টির ওপর await করা হয়েছে। এটি মেইন থ্রেড বা ইভেন্ট লুপকে ব্লক করবে না কারণ as_completed শুধুমাত্র সম্পন্ন হওয়া coroutine-ই সরবরাহ করে।

এই অ্যাসাইনমেন্টটি প্রয়োজনীয় কারণ পাইথনে exc ভেরিয়েবলের স্কোপ শুধুমাত্র সংশ্লিষ্ট except ব্লকের ভেতরেই সীমাবদ্ধ থাকে, কিন্তু এক্সেপশনের রেফারেন্সটি পরবর্তীতে ব্যবহারের জন্য সংরক্ষণ করা দরকার।

আগের নিয়মের মতোই এক্সেপশন অবজেক্টের রেফারেন্স সংরক্ষণ করা হয়েছে।

যদি কোনো এরর ঘটে থাকে, তবে স্ট্যাটাস DownloadStatus.ERROR সেট করা হয়েছে।

verbose মোডে, রেইজ হওয়া এক্সেপশন থেকে রিকোয়েস্ট ইউআরএলটি (URL) text হিসেবে এক্সট্রাক্ট করা হয়েছে...

...এবং কান্ট্রি কোড ডিসপ্লে করার জন্য ফাইলের নাম এক্সট্রাক্ট করা হয়েছে।

download_many ফাংশনটি supervisor coroutine object-টিকে instantiated করে এবং asyncio.run-এর মাধ্যমে ইভেন্ট লুপে পাঠায়, এরপর ইভেন্ট লুপ শেষ হলে supervisor যে কাউন্টার রিটার্ন করে তা সংগ্রহ করে।

অবজেক্ট ট্র্যাকিং এবং স্কোপিং মেকানিজম
Example 21-7-এ, ফিউচারের সাথে কান্ট্রি কোডের যে ম্যাপিং Example 20-16-এ দেখা গিয়েছিল তা ব্যবহার করা সম্ভব হয়নি, কারণ asyncio.as_completed দ্বারা রিটার্ন করা awaitable-গুলো সেই একই awaitable নয় যা as_completed কলের মধ্যে পাস করা হয়েছিল। internal মেকানিজমের কারণে, asyncio প্রদত্ত awaitable-গুলোকে অন্য কিছু অভ্যন্তরীণ ফিউচার অবজেক্ট দ্বারা প্রতিস্থাপন বা wrap করে দিতে পারে, যা শেষ পর্যন্ত একই ফলাফল তৈরি করবে।

ব্যর্থতার ক্ষেত্রে একটি ডিকশনারি থেকে কান্ট্রি কোডটি পুনরুদ্ধার করার জন্য awaitable-গুলোকে key হিসেবে ব্যবহার করা অসম্ভব ছিল দেখে, এক্সেপশন অবজেক্ট থেকেই কান্ট্রি কোড এক্সট্রাক্ট করতে হয়েছিল। সেটি করার জন্য, try/except স্টেটমেন্টের বাইরে এক্সেপশনটি পুনরুদ্ধার করতে error ভেরিয়েবলের মধ্যে এক্সেপশনটি write বা অ্যাসাইন করে রাখা হয়েছিল।

পাইথন কোনো block-scoped ভাষা নয়: লুপ (loops) এবং try/except-এর মতো স্টেটমেন্টগুলো তাদের পরিচালিত ব্লকের ভেতরে কোনো লোকাল স্কোপ (local scope) তৈরি করে না। কিন্তু যদি কোনো except ক্লজ একটি এক্সেপশনকে কোনো ভেরিয়েবলের সাথে যুক্ত বা বাইন্ড করে (যেমন পূর্বে দেখা exc ভেরিয়েবলগুলো)—তবে সেই যুক্ত থাকার বিষয়টি (binding) শুধুমাত্র ঐ নির্দিষ্ট except ক্লজের ভেতরের ব্লকেই সীমাবদ্ধ থাকে এবং ব্লক শেষে ভেরিয়েবলটি মেমোরি থেকে মুছে যায়।
"""