"""
Python normally runs code line by line in one single flow called the main thread.
When a program needs to do several things together (for example, download 10 files at once or read 20 files), it can
create extra threads. Each thread is like a separate worker that can run code independently. All threads inside one
Python program share the same memory, so they can easily pass data to each other.
"""

"""
-> The problem with creating threads manually
"""
# The standard way to create a thread is this code:
import threading

def my_task():
    print("Task is running.")

t = threading.Thread(target=my_task)
t.start()
t.join()
"""
If 100 tasks need to run, 100 threads must be created. Creating a thread takes time (a few milliseconds each).
Destroying a thread also takes time. The operating system has limits on how many threads one program can have.
If too many threads are created, the program slows down or crashes.
"""

"""
Q : What a thread pool solves?
-> A thread pool creates a fixed number of worker threads once at the beginning (for example, 5 or 10 workers).

These workers sit idle and wait for jobs. When a new task arrives, one of the waiting workers picks it up and 
immediately starts running the task function. To execute Python bytecode inside the function, that worker must 
acquire (or already hold) the GIL. If another thread currently holds the GIL, the worker waits until the GIL is 
released. Once the GIL is acquired then the worker executes Python code until the function finishes.

when create thread pool no new threads are created or destroyed during the program. This saves time and keeps the 
number of threads under control.
"""

"""
When a thread is not executing Python bytecode, it does not need the GIL.

Multiple I/O tasks execute in parallel (their waiting periods overlap), and each I/O task is handled by its own thread. 
These threads are not blocked by the GIL during the waiting part of I/O. Because these thread are not execute python
bytecode.

-> Suppose Our Code is like: 
response = requests.get("https://anik.com")      # blocking cz I/O task
data = file.read(1024)                           # blocking cz I/O task
result = socket.recv(4096)                       # blocking cz I/O task
time.sleep(5)                                    # blocking (special case) cz I/O task
conn, addr = server_socket.accept()              # blocking cz I/O task

Q : What actually happens during execute blocking I/O task?
-> When Our code calls something like: requests.get(url), file.read(), socket.recv(), time.sleep(3), cursor.execute(...) 
or cursor.fetchall() ... the thread stops moving forward right there. It hands the work over to the operating 
system(Windows, Linux, macOS) means it release GIL. like says: "Please do this slow thing for me. Wake me up when it's ready."

While waiting, that thread:
  - uses zero CPU
  - is not running any Python lines
  - is asleep in the kernel (operating system level)

This situation called blocking — the thread is blocked/paused/sleeping until the OS says "done".
"""

"""
Q : How Python provides a thread pool?
-> Python gives a ready-made thread pool in the standard library. The class name is ThreadPoolExecutor. ThreadPoolExecutor 
is a high-level API in Python (introduced in version 3.2) located within the concurrent.futures module. It is used to 
asynchronously execute callables (functions) using a pool of threads.
"""
print("\nExecution Start of Thread Pool Code.\n")

# Coding Example
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
        # print("Type of Future Object : ", type(future_object))
        # print("dir of future_object : ", future_object.__dir__())
        # print("dir of future_object : ", future_object.__dict__)
        submitted_futures.append(future_object)

    # wait for each task and retrieve its result
    for future_object in submitted_futures:
        result = future_object.result()     # blocks until the task finishes
        print("Result From Task : ", result)

"""
The `with` statement automatically calls shutdown(wait=True) when the block ends. This waits for all queued tasks to finish 
and then cleanly stops the worker threads. 

The max_workers argument sets the maximum number of simultaneous worker threads.  For I/O-bound tasks the value is often 
set to a number larger than the CPU count, for example 10 or 20. 

The submit method accepts a callable and its arguments, places the task into the queue, and returns a Future object 
immediately. submit() does not wait for the task to finish. The Future object is like a "promise" or "ticket": 
                "I will give you the result later when it's ready." 
The actual work (running worker function) happens in a background worker thread from the pool.

When future_object.result() is called, the calling thread pauses(stop moving forward/blocks) until one of the 
following conditions is met:
1. The background task associated with the Future has completed successfully, in which case result() returns the value 
returned by the task, or
2. An exception was raised during the execution of the background task, in which case result() re-raises that same 
exception in the calling thread.

This blocking behavior allows the program to wait for the result of an asynchronously executed task while keeping the 
code simple and readable.
"""

"""
-> Easiest way to run many tasks: .map()
"""
print("\nExecution Start of Thread Pool Map Code.\n")

with ThreadPoolExecutor(max_workers=4) as pool:
    numbers = [1, 2, 3, 4, 5, 6, 7, 8]
    results = pool.map(worker, numbers)
    results = list(results)

print("Result of Map Function : ", results)

"""
Q : What pool.map() actually does?
1. All tasks are submitted immediately
 - When pool.map(worker, numbers) is called, the method first creates a list of Future objects by running this logic internally:
                     fs = [pool.submit(worker, value) for value in numbers]
 - Every item in the iterable is submitted right away using submit().
 - With max_workers=4 and 8 items: The first 4 tasks start running immediately in the worker threads. The remaining 4 tasks are placed 
   in the internal queue and wait for a free worker.
 - There is no lazy submission. All tasks enter the pool before the method even returns an iterator.

2. It returns a generator (not a list)
 - After submission, map returns the result of a nested generator function (internally named result_iterator).
 - This generator holds the list of all Future objects in the original submission order.
 - At the exact moment the line results = pool.map(worker, numbers) is executed:
    - All tasks have already been submitted.
    - No task has finished yet (unless they were extremely fast).
    - The generator is simply waiting to be iterated; it has not yet called .result() on any future.

3. Results are collected by automatically calling .result() in order
When the returned generator is consumed (by list(), a for loop, or next()), results = list(results) the following happens for each item:
 - The generator takes the next Future in the original submission order.
 - It calls future.result() on that Future.
 - This call blocks the main thread until that specific task finishes.
 - Once the task completes, the result is yielded.
 - The generator moves to the next Future and repeats the process.
Because .result() is called strictly in submission order, the yielded results always appear in the same order as the input list, even if the 
worker threads finished the tasks in a completely different sequence.

4. Exception handling is automatic
 - If any task raises an exception, the generator raises that same exception exactly at the moment the corresponding result is requested.
 - Results before the finish task are returned normally. Results after the finish task are never processed (iteration stops)
"""