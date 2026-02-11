import os
import sys
from time import perf_counter
from typing import NamedTuple
from threading import Thread
from queue import Queue

from primes import is_prime, NUMBERS

class PrimeResult(NamedTuple):
    n: int
    prime: bool
    elapsed: float

jobQueue = Queue
ResultQueue = Queue

"""
threading-এর জন্য queue.Queue ব্যবহার করা হয়েছে। পাইথনের এই Queue লাইব্রেরিটি thread-safe। অর্থাৎ একাধিক thread যখন একসাথে 
এই queue থেকে ডেটা নেওয়ার (get) বা দেওয়ার (put) চেষ্টা করে তখন ডেটা নষ্ট হওয়া বা duplicate হওয়ার কোনো ভয় থাকে না।
"""

def check(n):
    t0 = perf_counter()
    res = is_prime(n)
    return PrimeResult(n, res, perf_counter() - t0)


def worker(jobs: jobQueue, results: ResultQueue):
    while n := jobs.get():
        results.put(check(n))
        jobs.task_done()

    results.put(PrimeResult(0, False, 0.0))
    jobs.task_done()

"""
-> task_done() হলো একটি Acknowledgment Signal। যখন কোনো একটি কাজ Queue থেকে get()-এর মাধ্যমে বের করে আনা হয়, তখন Queue 
স্বয়ংক্রিয়ভাবে জানে না যে ওই কাজটির প্রসেসিং শেষ হয়েছে কি না। task_done() কল করার মাধ্যমে কিউ-কে জানানো হয় যে, "আমি কিউ থেকে যে -
আইটেমটি নিয়েছিলাম, সেটির কাজ পুরোপুরি শেষ হয়েছে।"

এটি মূলত queue.join() মেথডের সাথে জোড়া হিসেবে কাজ করে। যদি প্রোগ্রামে join() ব্যবহার না করা হয়, তবে task_done() না দিলেও কোডটি 
চলবে, কিন্তু multi-threaded প্রোগ্রামে কাজের সমাপ্তি নিশ্চিত করার জন্য এটি অপরিহার্য।

Q : How task_done() work?
-> queue.Queue ক্লাসের ভেতরে একটি Internal Counter থাকে যা কাজ tracking করে। এর ধাপগুলো নিচে বর্ণনা করা হলো:
- Increment: যখনই put() মেথড ব্যবহার করে queue-তে কোনো নতুন data বা কাজ রাখা হয়, তখন queue-এর ভেতরের এই counter ১ করে বৃদ্ধি পায়।

- Decrement: যখন কোনো Worker Thread কাজ শেষ করে task_done() কল করে, তখন ওই counter-টি ১ করে কমে।

- Reach Zero: counter-টি কমতে কমতে যখন শূন্য (০) হয়, তখন queue বুঝে নেয় যে সব কাজ শেষ।

Q : Why need task_done()?
1. Thread Synchronization
Multi Threading-এ Main Thread অনেক সময় সব কাজ শেষ হওয়া পর্যন্ত অপেক্ষা করতে চায়। queue.join() মেথডটি ব্যবহার করলে main thread 
ততক্ষণ পর্যন্ত আটকে (Block) থাকে যতক্ষণ না queue-এর ভেতরের ওই কাউন্টারটি শূন্য হচ্ছে। যদি task_done() কল করা না হয়, তবে কাউন্টার 
কখনোই শূন্য হবে না এবং join() কল করা মেইন থ্রেডটি সারাজীবন আটকে থাকবে (Deadlock)।

2. Poison Pill and Cleaning
প্রদত্ত কোডে results.put(PrimeResult(0, False, 0.0)) দেওয়ার পর এবং লুপের ভেতরেও task_done() ব্যবহার করা হয়েছে। এটি নিশ্চিত করে 
যে প্রতিটি প্রসেস বা কাজের হিসাব কিউ ঠিকমতো রাখতে পারছে। লুপের বাইরের task_done() টি মূলত 'পয়জন পিল' বা শেষ সংকেতটির কাজ সম্পন্ন 
হয়েছে তা জানানোর জন্য ব্যবহৃত হয়।


-> যদি worker()-এ task_done() না থাকত, তবে প্রোগ্রামটি বুঝতে পারত না যে is_prime ফাংশনটি কাজ শেষ করেছে কি না। এর ফলে বড় 
কোনো সিস্টেমে resource leak হতে পারত অথবা মেইন থ্রেড কাজের সমাপ্তি না জেনেই প্রোগ্রাম বন্ধ করে দিতে পারত।

-> get() vs task_done()
get() কল করলে queue থেকে data বের হয়ে আসে ঠিকই, কিন্তু queue-এর ভেতরের কাজের কাউন্টারটি কমে না। queue মনে করে কাজ শুরু হয়েছে 
মাত্র। শুধুমাত্র task_done() call করলেই queue নিশ্চিত হয় যে কাজটির পেছনের সব logic সফলভাবে execute হয়েছে।
"""

def start_jobs(num_threads, jobs: jobQueue, results: ResultQueue):
    for n in NUMBERS:
        jobs.put(n)

    for _ in range(num_threads):
        thread = Thread(target=worker, args=(jobs, results))
        thread.start()

        jobs.put(0)


def report(num_threads, results: ResultQueue):
    checked, threads_done = 0, 0

    while threads_done < num_threads:
        n, prime, elapsed = results.get()

        if n == 0:
            threads_done += 1
        else:
            checked += 1
            label = 'P' if prime else ''
            print(f'{n:16} {label} {elapsed:9.6f}s')

    return checked


def main():
    if len(sys.argv) < 2:
        num_threads = os.cpu_count()
        print("Number of Thread : ", num_threads)
    else:
        num_threads = int(sys.argv[1])

    print(f'Checking {len(NUMBERS)} numbers with {num_threads} threads.')

    t0 = perf_counter()

    jobs: jobQueue = Queue()
    results: ResultQueue = Queue()

    start_jobs(num_threads, jobs, results)
    checked = report(num_threads, results)

    elapsed = perf_counter() - t0
    print(f'{checked} checks in {elapsed:.2f}s')

if __name__ == '__main__':
    main()


"""
এখানে MultiProcessing-এর বদলে threading ব্যবহার করা হয়েছে। এই দুই ধরনের কাজের জন্য পাইথনের API প্রায় একই রকম হওয়ায় একটি থেকে 
অন্যটিতে রূপান্তর করা বেশ সহজ। কিন্তু is_prime ফাংশনটি যেহেতু প্রচুর গণনামূলক বা ক্যালকুলেশন নির্ভর কাজ (compute-intensive) তাই পাইথনের 
GIL (Global Interpreter Lock)-এর কারণে এই threaded version-টি সাধারণ কোডের চেয়েও ধীরগতিতে চলে। থ্রেডের সংখ্যা যত বাড়ানো হয় 
প্রোগ্রামটি তত বেশি ধীর হয়ে যায়। এর কারণ হলো CPU Contention (একাধিক থ্রেড একই সময়ে সিপিইউ পাওয়ার জন্য প্রতিযোগিতা করা) এবং 
Context Switching (এক থ্রেড থেকে অন্য থ্রেডে যাওয়ার প্রক্রিয়া)-এর বাড়তি খরচ। যখন অপারেটিং সিস্টেম (OS) একটি থ্রেড বন্ধ করে অন্য থ্রেড 
চালু করে, তখন তাকে CPU-এর বর্তমান অবস্থা (Registers) সেভ করতে হয় এবং পরবর্তী কাজের অবস্থান (Program Counter) আপডেট করতে হয়। 
এই কাজগুলো করতে গিয়ে CPU-এর ক্যাশ মেমোরি খালি হয়ে যায় এবং অনেক সময় মেমোরি Swapping করতে হয়, যা পুরো প্রক্রিয়াকে অনেক ব্যয়বহুল বা 
ধীর করে দেয়।
"""

"""
# Context Switching and OS Mechanisms
Operating System যখন একটি চলমান Thread/Process থামিয়ে অন্য একটি Thread/Process শুরু করে, তখন বেশ কিছু জটিল ঘটনা ঘটে:

1. CPU Registers Save করা
CPU-এর ভেতরে খুব ছোট কিন্তু অত্যন্ত দ্রুত কিছু মেমোরি থাকে যেগুলোকে Registers বলা হয়। একটি thread যখন চলে তখন তার প্রয়োজনীয় সব 
তাৎক্ষণিক data এবং হিসাব এই রেজিস্টারে থাকে। যখন thread switch করা হয়, OS-কে এই রেজিস্টারের বর্তমান মানগুলো মেমোরিতে save করে 
রাখতে হয়, যাতে পরবর্তীতে ওই thread-টি আবার চালু হলে ঠিক যেখান থেকে শেষ হয়েছিল সেখান থেকেই শুরু করা যায়। এটি অনেকটা বই পড়ার 
সময় মাঝপথে মার্ক করে রাখার মতো।

2. Program Counter(PC)
এটি একটি বিশেষ register যা বলে দেয় CPU এরপর কোন লাইনটি execute করবে। যখন একটি থ্রেড থেকে অন্য থ্রেডে switch করা হয় (context 
switching) তখন OS বর্তমান থ্রেডের PC-এর মান সংরক্ষণ করে এবং নতুন থ্রেডের জন্য PC-তে তার পরবর্তী instruction-এর Address set করে দেয়।

3. Stack Pointer
প্রতিটি থ্রেডের নিজস্ব একটি মেমোরি এলাকা থাকে যাকে Stack বলে (যেখানে লোকাল ভ্যারিয়েবল থাকে)। OS-কে নতুন থ্রেডের স্ট্যাকের ঠিকানায় pointer-টি 
set করতে হয়।

4. Invalidating CPU Caches
CPU তার main memory (RAM) থেকে ডেটা নিতে অনেক সময় ব্যয় করে, তাই সে দ্রুত কাজ করার জন্য L1, L2, L3 Cache ব্যবহার করে। যখন 
thread-1 থেকে thread-2 তে switch করা হয়, তখন ক্যাশ মেমোরিতে থাকা thread-1 এর ডেটাগুলো thread-2 এর কোনো কাজে আসে না। ফলে 
CPU-কে cache থেকে পুরনো ডেটা ফেলে দিতে হয় এবং নতুন ডেটা reload করতে হয়। এই প্রক্রিয়াটি অত্যন্ত সময়সাপেক্ষ এবং একেই Cache 
Invalidation বলা হয়।

5. Swapping Memory Pages
Suppose পড়ার টেবিলে বসে কিছু কাজ করা হচ্ছে।
- টেবিল (RAM): এটি হলো কাজের জায়গা। এখানে শুধুমাত্র সেই বইগুলো রাখা যায় যেগুলো নিয়ে বর্তমানে কাজ চলছে। টেবিলটি ছোট কিন্তু এখান থেকে 
বই নিয়ে পড়া খুব সহজ এবং দ্রুত।
- আলমারি (Hard Disk): এটি বিশাল বড়। এখানে হাজার হাজার বই রাখা যায়। কিন্তু আলমারি থেকে একটি বই খুঁজে বের করে টেবিলে নিয়ে আসতে 
অনেক সময় লাগে।

এখন ধরা যাক টেবিলটি বইয়ে ভরে গেছে। কিন্তু নতুন একটি বিষয় পড়ার জন্য আরও একটি বই টেবিলের ওপর রাখা দরকার। তখন কী করতে হবে?.... টেবিল 
থেকে একটি পুরনো বই সরিয়ে আলমারিতে রেখে আসতে হবে, যাতে নতুন বইটির জন্য জায়গা হয়।

এই যে টেবিল/RAM থেকে আলমারিতে/Disk বই/Data সরিয়ে রাখা এবং দরকার পড়লে আবার ফেরত আনা এটিই হলো Swapping।

Q : What is Memory Page?
-> OS যখন কোনো Process বা Thread চালায় তখন সে পুরো ডাটাকে একবারে মেমোরিতে রাখে না। সে ডাটাকে ছোট ছোট নির্দিষ্ট আকারের ব্লকে ভাগ 
করে নেয়। এই প্রতিটি ব্লককে বলা হয় "Page" (সাধারণত ৪ কিলোবাইট সাইজের হয়)। যখন কোনো থ্রেড চলে তখন Os তার প্রয়োজনীয় কিছু পেজ RAM-এ 
load করে।

Q : How Swaping Work?
যখন সিস্টেমে অনেক বেশি process বা thread চালু হয়, তখন র‍্যামের জায়গা ফুরিয়ে আসতে থাকে। তখন OS নিচের ধাপগুলো অনুসরণ করে:
1. Page Out: OS দেখে কোন পেজটি বর্তমানে ব্যবহার হচ্ছে না বা অনেকক্ষণ ধরে অলস পড়ে আছে। 
2. সেই অব্যবহৃত পেজটিকে RAM থেকে মুছে দিয়ে হার্ডডিস্কের একটি নির্দিষ্ট জায়গায় (যাকে Swap Space বা Pagefile বলে) copy করে রেখে দেয়। এতে 
RAM-এ কিছু জায়গা খালি হয়। 
3. Page In: নতুন থ্রেডের প্রয়োজনীয় ডেটা বা পেজ তখন ওই খালি হওয়া র‍্যামের জায়গায় load করা হয়। 
4. পরবর্তীতে যদি সেই পুরনো thread-টি আবার কাজ শুরু করতে চায়, তখন OS-কে আবার disk থেকে ওই পেজটি খুঁজে RAM-এ নিয়ে আসতে হয়।

# Speed Difference
- RAM থেকে Data পড়তে কয়েক Nanosecond সময় লাগে।
- HardDisk(HDD) বা SSD থেকে Data পড়তে কয়েক Millisecond সময় লাগে।

একটি Disk র‍্যামের তুলনায় প্রায় ১০ লক্ষ গুণ বেশি ধীর হতে পারে। ফলে যখন OS বারবার disk থেকে র‍্যামে Data আনা-নেওয়া করে, তখন CPU-কে 
অধিকাংশ সময় বসে থাকতে হয় ডিস্কের ডেটার জন্য। একে বলা হয় "Disk I/O Wait"।

যদি Swapping খুব বেশি পরিমাণে হতে থাকে, তবে কম্পিউটার প্রায় অকেজো হয়ে পড়ে যাকে Thrashing বলা হয়।
"""