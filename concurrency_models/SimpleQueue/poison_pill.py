"""
যখন একটি worker ফাংশন while True বা লুপের মধ্যে থাকে তখন সে জানে না কখন ডেটা আসা বন্ধ হবে। সে সারাক্ষণ get() করার জন্য অপেক্ষা
করে। প্রোগ্রামটি চিরস্থায়ীভাবে আটকে থাকা (Deadlock) থেকে বাঁচাতে একটি সংকেত পাঠানো হয় যাকে প্রোগ্রামিংয়ের ভাষায় Poison Pill বা Sentinel
Value বলা হয়।

1. Sending Signal: Main Process সব কাজ শেষ করার পর Queue-তে এমন একটি মান রাখে যা সাধারণ কাজের মানের চেয়ে আলাদা (যেমন: 0 বা None)।
2. Check Condition: Worker যখন এই বিশেষ মানটি (যেমন 0) পায়, তখন সে বুঝতে পারে যে আর কোনো কাজ বাকি নেই।
3. Process Stop: এরপর Worker loop থেকে break করে এবং process-টি সফলভাবে শেষ হয়।
"""

from multiprocessing import Process, SimpleQueue

def worker(jobs, results):
    while True:
        n = jobs.get()
        if n == 0:      # its Poison Pill
            break

        results.put(n*n)


if __name__ == '__main__':
    jobs = SimpleQueue()
    results = SimpleQueue()

    num_worker = 3
    processes = []

    for _ in range(num_worker):
        p = Process(target=worker, args=(jobs, results))
        p.start()

        processes.append(p)

    tasks = [10, 20, 30, 40, 50]
    for t in tasks:
        jobs.put(t)

    # প্রতিটি Worker-এর জন্য একটি করে '0' পাঠানো (Poison Pill)
    for _ in range(num_worker):
        jobs.put(0)

    for _ in range(len(tasks)):
        print(f'Result : {results.get()}')

    for p in processes:
        p.join()

    print('And of all task and Processes are closed.')
