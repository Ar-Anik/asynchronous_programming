import asyncio
import socket
from keyword import kwlist

MAX_KEYWORD_LEN = 4

async def probe(domain: str) -> tuple[str, bool]:
    loop = asyncio.get_running_loop()

    try:
        await loop.getaddrinfo(domain, None)
    except socket.gaierror:
        return (domain, False)

    return (domain, True)

"""
asyncio.get_running_loop() ফাংশনটির কাজ হলো বর্তমান OS thread-এ যে event loop সচল আছে, সেটিকে খুঁজে বের করা এবং সেটির একটি রেফারেন্স রিটার্ন করা।

asyncio-তে সব asynchronous কাজ একটি কেন্দ্রীয় লুপের মাধ্যমে পরিচালিত হয়। এই কোডে probe ফাংশনের ভেতরে ডোমেইন রেজোলিউশন করার জন্য লুপের নিজস্ব কিছু মেথড (যেমন: getaddrinfo) ব্যবহার করা প্রয়োজন। সেই সচল লুপটিকে ধরার জন্যই এই ফাংশনটি কল করা হয়েছে। যদি কোনো লুপ সচল না থাকে, তবে এটি একটি RuntimeError তৈরি করে।
"""

"""
-> getaddrinfo(domain, None)
এটি মূলত একটি low-level নেটওয়ার্কিং মেথড যা একটি ডোমেইন নামকে (যেমন: logic.dev) তার সংশ্লিষ্ট IP address-এ রূপান্তর করার চেষ্টা করে। একে DNS Resolution বলা হয়।
- domain: এটি সেই ডোমেইন নাম যা পরীক্ষা করা হচ্ছে।
- None: এখানে দ্বিতীয় আর্গুমেন্টটি সাধারণত একটি 'service' বা পোর্ট নাম্বার (যেমন 'http' বা 80) নির্দেশ করে। যেহেতু এখানে শুধুমাত্র ডোমেইনটি বিদ্যমান কি না তা যাচাই করা হচ্ছে, তাই কোনো নির্দিষ্ট পোর্টের প্রয়োজন নেই বলে None ব্যবহার করা হয়েছে।

যখন এই মেথডটি সফলভাবে execute হয়, তখন বোঝা যায় ডোমেইনটি ইন্টারনেটে সক্রিয় আছে।
"""

"""
socket.gaierror হলো "Get Address Info Error"-এর সংক্ষিপ্ত রূপ। এটি একটি নির্দিষ্ট ধরণের exception যা নেটওয়ার্কিং সংক্রান্ত কাজের সময় ঘটে।

যখন getaddrinfo ফাংশনটি কোনো ডোমেইন নামের বিপরীতে কোনো IP address খুঁজে পায় না (অর্থাৎ ডোমেইনটি যদি রেজিস্টার্ড না থাকে বা ভুল হয়), তখন system এই error প্রদান করে।

কোডটিতে try...except socket.gaierror ব্লক ব্যবহার করা হয়েছে একটি logic check হিসেবে।
- যদি ডোমেইনটি পাওয়া যায়, তবে probe ফাংশনটি True রিটার্ন করে।
- যদি ডোমেইনটি খুঁজে না পাওয়া যায় এবং socket.gaierror ঘটে, তখন কোডটি ক্র্যাশ না করে সরাসরি except ব্লকে চলে যায় এবং False রিটার্ন করে। এটি মূলত একটি validation প্রসেস হিসেবে কাজ করছে।
"""

async def main() -> None:
    names = (kw for kw in kwlist if len(kw) <= MAX_KEYWORD_LEN)
    domains = (f'{name}.dev'.lower() for name in names)
    coros = [probe(domain) for domain in domains]

    for coro in asyncio.as_completed(coros):
        domain, found = await coro
        mark = '+' if found else ' '
        print(f'{mark} {domain}')


if __name__ == '__main__':
    asyncio.run(main())

"""
-> asyncio.as_completed(coros)
asyncio.as_completed একটি iterator রিটার্ন করে, যা অনেকগুলো asynchronous কাজকে সমান্তরালভাবে পরিচালনা করার সময় দক্ষতা বৃদ্ধি করে।

যখন অনেকগুলো coroutine (এখানে coros লিস্টটি) একসাথে রান করা হয়, তখন সব কাজ একই সময়ে শেষ হয় না। কোনটি আগে শেষ হবে তা নির্ভর করে নেটওয়ার্ক স্পিড বা সার্ভারের রেসপন্সের ওপর। as_completed ব্যবহার করলে:
- এটি পুরো sequence শেষ হওয়া পর্যন্ত অপেক্ষা করে না।
- যে কাজ বা coroutine সবার আগে শেষ হবে, সেটিকেই সবার আগে await করার সুযোগ দেয়।
- এর ফলে আউটপুট পাওয়ার জন্য লজিক্যাল কোনো সিরিয়াল মেইনটেইন করতে হয় না, যা প্রোগ্রামের গতি বাড়িয়ে দেয়।

Suppose, ৫টি ডোমেইন চেক করা হচ্ছে। ডোমেইন 'A' এর রেসপন্স পেতে ৫ সেকেন্ড লাগে এবং ডোমেইন 'B' এর রেসপন্স পেতে ২ সেকেন্ড লাগে। যদি as_completed ব্যবহার করা হয়, তবে ২ সেকেন্ড শেষ হওয়া মাত্রই ডোমেইন 'B' এর রেজাল্ট পাওয়া যাবে। ডোমেইন 'A' এর জন্য বসে থাকতে হবে না।

নেটওয়ার্ক I/O অপারেশনগুলোতে ল্যাটেন্সি থাকে। কোনো ডোমেইন সার্ভার দ্রুত রেসপন্স দেয়, কোনটি দেরি করে। as_completed এই ভিন্নতাকে কাজে লাগিয়ে দ্রুততম রেজাল্টগুলো আগে প্রসেস করার সুযোগ দেয়, ফলে সামগ্রিক system-এর কার্যকারিতা বৃদ্ধি পায়। এটি অনেকটা "First come, first served" নীতির মতো কাজ করে।
"""

"""
concurrent.futures.as_completed যখন কল করা হয়, তখন এটি যে থ্রেডে রান করছে সেই থ্রেডকে পুরোপুরি আটকে (block) দেয় যতক্ষণ না কোনো একটি future object রেজাল্টসহ ফিরে আসে। অর্থাৎ, এটি একটি synchronous ব্লকিং অপারেশন।

কিন্তু asyncio.as_completed এর ক্ষেত্রে বিষয়টি ভিন্ন:
এটি মূল ইভেন্ট লুপ বা system-কে ব্লক করে না। পরিবর্তে, এটি একটি iterator রিটার্ন করে। যখন for লুপের ভেতরে await করা হয়, তখন শুধুমাত্র ওই নির্দিষ্ট 
coroutine-টি (যেমন: main()) সাময়িকভাবে স্থগিত থাকে। এই সময়ে ইভেন্ট লুপ তার internal মেকানিজম ব্যবহার করে অন্যান্য কাজ বা নেটওয়ার্ক রিকোয়েস্ট execute 
করতে পারে।
লুপটি ততক্ষণই অপেক্ষা করে যতক্ষণ না অন্তত একটি coroutine তার কাজ শেষ করে। তবে এই অপেক্ষাটি "সহযোগিতামূলক" (cooperative), অর্থাৎ এটি লুপের অন্যান্য 
কাজের পথ বন্ধ করে দেয় না।
"""

# asyncio.as_completed এর Equivalent Pseudo-code
# asyncio.as_completed(coros) এর একটি কাল্পনিক ইন্টারনাল রিপ্রেজেন্টেশন
def as_completed_logic(coros):
    # ১. সব coroutine-কে Task হিসেবে শিডিউল করা হয়
    tasks = [asyncio.ensure_future(c) for c in coros]

    # ২. একটি ইন্টারনাল কিউ (Queue) মেইনটেইন করা হয় যেখানে শেষ হওয়া টাস্কগুলো জমা হবে
    done_queue = asyncio.Queue()

    # ৩. প্রতিটি টাস্ক শেষ হলে যেন কিউতে জমা হয়, সেজন্য callback সেট করা হয়
    def _on_completion(fut):
        done_queue.put_nowait(fut)

    for t in tasks:
        t.add_done_callback(_on_completion)

    # ৪. লুপ চালিয়ে একটি একটি করে রেজাল্ট yield করা হয়
    for _ in range(len(tasks)):
        # এটি একটি বিশেষ 'waiter' future প্রদান করে যা পরবর্তী টাস্ক শেষ হওয়া পর্যন্ত অপেক্ষা করে
        yield wait_for_next_done_task(done_queue)

"""
এখানে as_completed এর internal প্রসেসটি বিশ্লেষণ করা হলো:

টাস্ক র‍্যাপিং (Wrapping): আপনি যখন coros (লিস্ট অফ কোরাউটিন) ইনপুট দেন, তখন system সাথে সাথে সেগুলোকে Tasks হিসেবে কনভার্ট করে ফেলে। এর ফলে সবগুলো কোরাউটিন প্রায় একই সাথে execute হওয়া শুরু করে।

রেডি স্টেট (Ready State): as_completed একটি সাধারণ for লুপের মতো কাজ করে, কিন্তু এর ভেতরে থাকা yield করা অবজেক্টগুলো হলো "Proxy Futures"।

অপেক্ষার নীতি: যখন কোডে await coro (লুপের ভেতরে) করা হয়, তখন ইভেন্ট লুপ চেক করে ইন্টারনাল কিউতে কোনো টাস্ক শেষ হয়ে জমা হয়েছে কি না।

ডেলিগেশন (Delegation): যদি কোনো টাস্ক শেষ না হয়ে থাকে, তবে এটি কন্ট্রোল ইভেন্ট লুপের কাছে delegate করে দেয়। যখনই কোনো একটি টাস্ক (child) শেষ হয়, সেটি সবার আগে কিউ থেকে বের হয়ে আপনার await-এর কাছে চলে আসে।
"""

"""
এখানে "Proxy Future" বা "Waiter Future" বলতে একটি মধ্যবর্তী (intermediate) Future object-কে বোঝানো হয়েছে।

as_completed লুপের ভেতরে সরাসরি দেওয়া মূল coroutine-গুলোকে রিটার্ন করে না।

পরিবর্তে, এটি একটি নতুন Future object তৈরি করে yield করে।

এই বিশেষ Future-টি ইভেন্ট লুপের সাথে সংযুক্ত থাকে এবং নজর রাখে কখন আসল টাস্কগুলোর মধ্যে কোনো একটি শেষ হবে।

যে টাস্কটি সবার আগে শেষ হয়, এই Proxy Future-টি সেই টাস্কের রেজাল্টটি ধারণ করে ফেলে।
"""