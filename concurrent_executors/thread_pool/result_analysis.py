from concurrent.futures import ThreadPoolExecutor
import time

def worker(number):
    print(f"Worker {number} started.")
    time.sleep(2)
    print(f"Worker {number} finished.")
    return number * 10

# create a pool with 3 worker threads
with ThreadPoolExecutor(max_workers=3) as pool:

    # submit 8 task to the pool
    submitted_futures = []
    for i in range(8):
        future_object = pool.submit(worker, i)
        submitted_futures.append(future_object)

    # wait for each task and retrieve its result
    for future_object in submitted_futures:
        result = future_object.result()     # blocks until the task finishes
        print("Result From Task : ", result)

"""
# Result : 
Worker 0 started.
Worker 1 started.
Worker 2 started.
Worker 2 finished.
Worker 3 started.
Worker 0 finished.
Worker 4 started.
Worker 1 finished.
Worker 5 started.
Result From Task :  0
Result From Task :  10
Result From Task :  20
Worker 4 finished.
Worker 5 finished.
Worker 6 started.

Worker 7 started.
Worker 3 finished.
Result From Task :  30
Result From Task :  40
Result From Task :  50
Worker 6 finished.
Worker 7 finished.
Result From Task :  60
Result From Task :  70
"""

"""
In the above code 8 tasks are submitted, That means 8 Future objects are created, one for each task.

At the start the pool has 3 workers, so these 3 tasks begin immediately:
 - worker(0)
 - worker(1)
 - worker(2)

That is why the output begins with:
 - Worker 0 started.
 - Worker 1 started.
 - Worker 2 started.
 
Each worker does time.sleep(2), During sleep() the thread is not using the CPU. In CPython sleep() releases the GIL, 
so another thread can run.

As soon as one worker completes, that same worker thread takes the next waiting task from the queue. So the pattern becomes:
 - worker thread 0 finishes task 0, then starts task 3
 - worker thread 1 finishes task 1, then starts task 4
 - worker thread 2 finishes task 2, then starts task 5

Then later:
 - one free worker starts task 6
 - another free worker starts task 7

The printed Result From Task lines appear in order. This part is important:
    for future_object in submitted_futures:
        result = future_object.result()
        print("Result From Task : ", result)

This loop waits in submission order:
 - waits for future 0
 - then future 1
 - then future 2
 - then future 3
 - and so on
So even if task 2 finishes before task 0, the main thread still waits for task 0 first. That is why result printing 
can look different from task finishing order.
"""

