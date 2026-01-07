from multiprocessing import Process, SimpleQueue
import time

def worker(q):
    print('Worker Start...', time.perf_counter())
    data = q.get()
    print('Worker Get Data...', time.perf_counter())

    print(f'Process Start : ', data)
    time.sleep(1)
    print(f'Process End.')


if __name__ == '__main__':
    my_queue = SimpleQueue()

    p = Process(target=worker, args=(my_queue,))
    p.start()

    time.sleep(1)
    my_queue.put('Task-1')
    p.join()

"""
যখন p.start() কল করা হয় তখন worker ফাংশনটি একটি আলাদা প্রসেসে চলতে শুরু করে :

- Waiting : worker ফাংশনের ভেতর যখনই q.get() লাইনটি কার্যকর হয়, তখন প্রসেসটি সেখানে stack হয়ে যায়। কারণ তখন পর্যন্ত my_queue 
একদম খালি। একে প্রোগ্রামিংয়ের ভাষায় "Blocking" বলা হয়।

- Get Data : মেইন process যখন my_queue.put("Task-1") call করে Queue-তে ডেটা পাঠায়, ঠিক তখনই q.get() তার অপেক্ষার অবসান ঘটায়।

- Active হওয়া: Data পাওয়ার সাথে সাথে ওই ডেটা data ভেরিয়েবলে জমা হয় এবং এর পরের লাইনগুলো (যেমন: print, time.sleep) execute হতে শুরু করে।
"""

"""
যদি মেইন প্রসেস কখনো put() না করে এবং worker প্রসেস get() করার জন্য অপেক্ষা করতে থাকে তবে প্রোগ্রামটি অনির্দিষ্টকালের জন্য stack হয়ে থাকবে। 
একে Deadlock বলা হয়। এ কারণেই কাজ শেষে প্রসেস বন্ধ করতে 0 বা None (Poison Pill) পাঠানো হয়।
"""
