"""
যখন computing-এর কাজগুলো বিভিন্ন Threads বা Processes কে দেওয়া হয় তখন code সরাসরি কোনো worker function-কে call করে
return value পায় না। পরিবর্তে এই worker-গুলো Thread বা Process লাইব্রেরি দ্বারা নিয়ন্ত্রিত হয়। তাদের কাজের ফলাফল কোথাও জমা রাখা
প্রয়োজন। Concurrent programming এবং distributed systems-এ এই কাজের সমন্বয় করা এবং ফলাফল সংগ্রহ করার জন্য Queue ব্যবহার
করা একটি বহুল প্রচলিত পদ্ধতি।
"""

import sys
from time import perf_counter
from typing import NamedTuple
from multiprocessing import Process, SimpleQueue, cpu_count
from multiprocessing import queues

from primes import is_prime, NUMBERS

class PrimeResult(NamedTuple):
    n: int
    prime: bool
    elapsed: float


JobQueue = queues.SimpleQueue[int]
ResultQueue = queues.SimpleQueue[PrimeResult]
"""
JobQueue and ResultQueue হলো Type Alias. এটি কোনো কাজ করে না এটি শুধু পাইথনকে বলে দেয় যে "JobQueue মানে হলো Integer 
রাখার একটি Queue", "ResultQueue মানে হলো PrimeResult রাখার একটি Queue"। এটি অনেকটা একটি ক্যাটাগরি বা ক্লাসের মতো।
"""

def check(n):
    t0 = perf_counter()
    res = is_prime(n)

    return PrimeResult(n, res, perf_counter() - t0)


def worker(jobs: JobQueue, results: ResultQueue):
    while n := jobs.get():      # Walrus Operator use for poison pill
        results.put(check(n))

    results.put(PrimeResult(0, False, 0.0))

"""
যখন কোনো Worker process Queue থেকে 0 পায়, তখন Walrus অপারেটরের কারণে while লুপটি বন্ধ হয়ে যায়। কিন্তু লুপ বন্ধ হওয়া মানেই হলো 
ওই নির্দিষ্ট ওয়ার্কারটির কাজ পুরোপুরি শেষ। Main Process (যেটি ফলাফল সংগ্রহ করছে) কীভাবে জানবে যে একজন Worker তার কাজ শেষ করে বিদায় 
নিয়েছে?

এই কারণেই লুপের বাইরে এসে Worker-টি results Queue-তে একটি বিশেষ Final Sentinel পাঠিয়ে দেয়। এখানে 
PrimeResult(0, False, 0.0) হলো সেই Sentinel।

আর এই result catch করে report function টি, 
n, prime, elapsed = results.get()
if n == 0:
 procs_done += 1

"""

def start_jobs(procs: int, jobs: JobQueue, results: ResultQueue):
    for n in NUMBERS:
        jobs.put(n)

    for _ in range(procs):
        proc = Process(target=worker, args=(jobs, results))
        proc.start()

        jobs.put(0)      # poison pill

"""
1. type hinting এর সীমাবদ্ধতা: multiprocessing.SimpleQueue আসলে একটি মেথড যা সরাসরি type hint হিসেবে ব্যবহার করা যায় না। 
এটি মূলত একটি লো-লেভেল ক্লাসের সাথে যুক্ত।  not directly support : multiprocessing.SimpleQueue[int]. so use 
multiprocessing.queues.SimpleQueue[int]

2. টাইপ হিন্টের সমাধান: টাইপ হিন্টিং এর জন্য multiprocessing.queues থেকে SimpleQueue ক্লাসটি আলাদাভাবে ইম্পোর্ট করা হয়েছে।

3. ফলাফল সংরক্ষণের কাঠামো: PrimeResult একটি NamedTuple যেখানে পরীক্ষা করা number n এবং ফলাফল একসাথে রাখা হয়। এতে পরবর্তীতে 
ফলাফল প্রদর্শন করা সহজ হয়।

4. Jobs Queue (JobQueue): এটি একটি Type Alias। Main ফাংশন এই Queue ব্যবহার করে worker প্রসেসগুলোর কাছে সংখ্যাগুলো পাঠায়।

5. Result Queue (ResultQueue): এটি দ্বিতীয় একটি Queue যা সব ওয়ার্কারের কাছ থেকে পাওয়া ফলাফলগুলো সংগ্রহ করে।

6. check function: এটি সাধারণ Sequential কোডের মতোই কাজ করে যা একটি number prime কি না তা পরীক্ষা করে।

7. ওয়ার্কারের ভূমিকা: worker ফাংশনটি দুটি Queue গ্রহণ করে—একটি থেকে সে কাজ(Number) নেয় এবং অন্যটিতে ফলাফল জমা দেয়।

8. Poison Pill: এখানে 0 সংখ্যাটিকে 'Poison Pill' বা সংকেত হিসেবে ব্যবহার করা হয়েছে। Queue থেকে 0 পাওয়া মানে হলো ওই ওয়ার্কারের 
কাজ শেষ এবং লুপটি বন্ধ করতে হবে।

9. কাজ সম্পন্ন করা: সংখ্যাটি 0 না হলে সেটি পরীক্ষা করা হয় এবং ফলাফল results কিউতে পাঠানো হয়।

10. সমাপ্তি সংকেত পাঠানো: যখন একটি worker কাজ শেষ করে, তখন সে main লুপকে জানানোর জন্য একটি বিশেষ PrimeResult পাঠায়।

11. প্রসেস সংখ্যা: procs প্যারামিটারটি নির্ধারণ করে একসাথে কয়টি প্রসেস সমান্তরালভাবে চলবে।

12. কাজ সাজানো: শুরুতে সব সংখ্যাকে jobs কিউতে রাখা হয়।

13. চাইল্ড প্রসেস তৈরি: প্রতিটি ওয়ার্কারের জন্য আলাদা চাইল্ড প্রসেস তৈরি করা হয়। এরা ততক্ষণ কাজ করে যতক্ষণ না Queue থেকে 0 পায়।

14. প্রসেস শুরু: প্রতিটি চাইল্ড প্রসেসকে কাজ শুরুর নির্দেশ দেওয়া হয়।

15. টার্মিনেশন সংকেত: প্রতিটি প্রসেসের জন্য একটি করে 0 কিউতে পাঠানো হয় যাতে তারা কাজ শেষে বন্ধ হয়ে যায়।
"""

"""
Concurrent প্রোগ্রামিংয়ে Worker ফাংশনগুলো সাধারণত একটি indefinitely লুপে চলে। Queue থেকে আইটেম নেওয়া এবং প্রসেস করার এই 
প্রক্রিয়া ততক্ষণ চলে যতক্ষণ না একটি বিশেষ মান বা সংকেত পাওয়া যায়। এই বিশেষ মানটিকে বলা হয় Sentinel Value বা সংকেত মান। যখন 
এই সংকেতটি কোনো প্রসেসকে বন্ধ করার জন্য ব্যবহার করা হয় তখন একে Poison Pill।

1. None 
যদি ডেটার ভেতরেই None থাকার সম্ভাবনা থাকে তবে Sentinel হিসেবে None ব্যবহার করলে সমস্যা হয়।

Example: মনে করা যাক একটি প্রোগ্রামে কিছু মানুষের বয়স প্রসেস করা হচ্ছে। কারও বয়স জানা না থাকলে সেখানে None লেখা হয়।
Data list : [25, 30, None, 40, STOP]

এখানে যদি None-এর উপর depend করে program stop করা হয় তবে প্রোগ্রাম 30 এর পরেই থেমে যাবে। পরের 40 সংখ্যাটি আর প্রসেস হবে না।

2. object()
threading-এর ক্ষেত্রে object() কাজ করলেও মাল্টিপ্রসেসিংয়ে কাজ করে না। কারণ পাইথনে যখন এক প্রসেস থেকে অন্য প্রসেসে কিছু পাঠানো হয় তখন 
সেটি Pickling/serialized হয়ে যায়।

# Main Process:
SENTINEL = object()
queue.put(SENTINEL)

# When Worker Process Receive Object:
item = queue.get()
if item is SENTINEL: 
    print("Stop Process")
else:
    print("They are not same object.")

এখানে item is SENTINEL ফলাফল দেবে False। কারণ Serialization-এর পর অন্য প্রসেসে যখন object-টি পৌঁছায় তখন সেটি মেমরিতে সম্পূর্ণ 
নতুন একটি অবজেক্ট হিসেবে তৈরি হয়। ফলে is keyword দিয়ে তুলনা করলে সেটি আর match করে না।

3. Ellipsis (...)
পাইথনে ... বা Ellipsis হলো একটি Singleton object। অর্থাৎ পুরো python সিস্টেমে এর একটাই identity। এটি যে প্রসেসেই যাক না কেন 
এর identity একই থাকে।

# Main Process:
queue.put(...)

# Worker Process:
item = queue.get()
if item is ...:     # এটি সবসময় True হবে
    break

এটি Serialization-এর পরেও নিজের মূল identity ধরে রাখতে পারে তাই multi-processing এটি Sentinel হিসেবে খুব জনপ্রিয়।
"""

def report(procs: int, results: ResultQueue):
    checked, process_done = 0, 0

    while process_done < procs:
        n, prime, elapsed = results.get()

        if n == 0:
            process_done += 1
        else:
            checked += 1
            label = 'P' if prime else ''
            print(f'{n:16} {label} {elapsed:9.6f}s')

    return checked


def main():
    if len(sys.argv) < 2:
        procs = cpu_count()
    else:
        procs = int(sys.argv[1])

    print(f'Checking {len(NUMBERS)} numbers with {procs} processes:')

    t0 = perf_counter()

    jobs: JobQueue = SimpleQueue()
    results: ResultQueue = SimpleQueue()

    start_jobs(procs, jobs, results)

    checked = report(procs, results)

    elapsed = perf_counter() - t0
    print(f'{checked} checks in {elapsed:.2f}s')

"""
sys.argv হলো পাইথনের sys মডিউলের একটি ভেরিয়েবল। এর পূর্ণরূপ হলো Argument Vector। যখন একটি python script terminal বা 
command line থেকে চালানো হয় তখন ফাইলের নামের পরে যে শব্দ বা সংখ্যাগুলো দেওয়া হয় python সেগুলোকে এই লিস্টে জমা করে।

এর গঠন পদ্ধতি:
    - sys.argv[0]: এটি সবসময় স্ক্রিপ্ট বা ফাইলের নাম নির্দেশ করে।
    - sys.argv[1]: এটি ব্যবহারকারীর দেওয়া প্রথম আর্গুমেন্ট।
    - sys.argv[2]: এটি দ্বিতীয় আর্গুমেন্ট, এবং এভাবে পর্যায়ক্রমে চলতে থাকে।

টার্মিনালে python file-টি চালানোর সময় ফাইলের নামের পর স্পেস দিয়ে আর্গুমেন্টগুলো লিখতে হয়।

Normal Format: python file_name.py Argument_1 rgument_2
Example : python procs.py 4

command-line থেকে যাই পাঠানো হোক না কেন (যেমন সংখ্যা 4), python সেটিকে সবসময় String হিসেবে গ্রহণ করে। এই কারণে sys.argv[1]-কে 
int() ফাংশন দিয়ে পূর্ণসংখ্যায় রূপান্তর করা হয়েছে যাতে সেটি calculation-এর কাজে (প্রসেস সংখ্যা নির্ধারণে) ব্যবহার করা যায়।
"""

"""
jobs: JobQueue = SimpleQueue() এই লাইনটি দুটি আলাদা কাজ একসাথে করছে:

1. jobs: JobQueue: এখানে পাইথনের টাইপ চেকারকে (যেমন Mypy বা IDE) সংকেত দেওয়া হচ্ছে যে, jobs নামক এই ভেরিয়েবলটি অবশ্যই 
একটি JobQueue (অর্থাৎ queues.SimpleQueue[int]) হতে হবে। এটি একটি Condition বা প্রতিশ্রুতি মাত্র।

2. = SimpleQueue(): এটি হলো main কাজ। এখানে SimpleQueue() ক্লাসটি call করার মাধ্যমে কম্পিউটারের মেমরিতে একটি orginal Queue 
object তৈরি করা হচ্ছে।
"""


if __name__ == '__main__':
    main()

"""
# main function
1. প্রসেস সংখ্যা নির্ধারণ: যদি কমান্ড-লাইন থেকে কোনো আর্গুমেন্ট দেওয়া না হয় তবে কম্পিউটার বা সিস্টেমের মোট CPU কোরের সমপরিমাণ প্রসেস সেট 
করা হয়। অন্যথায় কমান্ড-লাইনে দেওয়া সংখ্যা অনুযায়ী প্রসেস তৈরি করা হয়।

2. Queue create: কাজের তালিকা পাঠানোর জন্য jobs এবং ফলাফল সংগ্রহের জন্য results নামে দুটি কিউ ব্যবহার করা হয়।

3. start job: start_jobs ফাংশনের মাধ্যমে প্রসেসগুলো চালু করা হয় যাতে তারা কাজ সম্পন্ন করে ফলাফলগুলো Queue-তে পাঠাতে পারে।

4. Report গ্রহণ: report ফাংশনটি কল করে ফলাফলগুলো সংগ্রহ করা হয় এবং স্ক্রিনে দেখানো হয়।

5. Time Count: কতগুলো সংখ্যা পরীক্ষা করা হলো এবং পুরো প্রক্রিয়াটিতে মোট কত সেকেন্ড সময় লাগলো তা শেষে প্রদর্শন করা হয়।


# report function
1. ইনপুট: এটি প্রসেস Number এবং ফলাফল আসার Queue-টি গ্রহণ করে।

2. loop condition: যতক্ষণ না সবগুলো প্রসেস তাদের কাজ শেষ করার সংকেত পাঠাচ্ছে, ততক্ষণ এই লুপ চলতে থাকে।

3. Data Collect: .get() মেথড ব্যবহার করে Queue থেকে একটি করে ফলাফল নেওয়া হয়। কিউতে কোনো ডেটা না আসা পর্যন্ত এটি Block করে থাকে।

4. Sentinal শনাক্তকরণ: যদি প্রাপ্ত ডেটাতে সংখ্যার মান 0 হয় তবে বোঝা যায় একটি প্রসেস তার সব কাজ শেষ করে বন্ধ হয়ে গেছে। তখন 
procs_done এর হিসাব এক বাড়ানো হয়।

5. Result Show: প্রাপ্ত ডেটা যদি 0 না হয়, তবে সেটি একটি সফল পরীক্ষা হিসেবে গণ্য করা হয় এবং নির্দিষ্ট ফরম্যাটে ফলাফলটি স্ক্রিনে প্রিন্ট করা হয়।
"""

"""
Result Order: কাজগুলো প্যারালালভাবে চলে বলে ফলাফলগুলো জমা দেওয়ার সিরিয়াল অনুযায়ী ফিরে আসে না। এই কারণেই প্রতিটি ফলাফলের সাথে 
মূল Number-টি n যুক্ত রাখা হয়েছে, যাতে বোঝা যায় কোন ফলাফলটি কোন সংখ্যার জন্য।

Debugging এবং Error: সব প্রসেস শেষ হওয়ার আগে মেইন প্রসেস বন্ধ হয়ে গেলে বিভিন্ন অভ্যন্তরীণ লক সমস্যার কারণে FileNotFoundError এর 
মতো বিভ্রান্তিকর error দেখা দিতে পারে। মাল্টিপ্রসেসিং debug or manage করা বেশ জটিল। এর চেয়ে ProcessPoolExecutor ব্যবহার করা অনেক 
বেশি সহজ এবং শক্তিশালী
"""
