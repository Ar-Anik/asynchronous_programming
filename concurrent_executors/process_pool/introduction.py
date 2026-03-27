"""
When a program needs to perform heavy mathematical calculations or process massive amounts of data, it can
create extra processes. Each process is an entirely separate instance of the Python interpreter with its own
memory space. Because memory is not shared, processes do not interfere with each other's data directly, but
they require explicit communication channels to pass data back and forth.
"""

"""
-> The problem with creating processes manually
"""
# The standard way to create a process is this code:
import multiprocessing

def my_task():
    print("Task is running.")

if __name__ == '__main__':
    p = multiprocessing.Process(target=my_task)
    p.start()
    p.join()

"""
If 100 heavy tasks need to run, 100 processes must be created. Creating a process takes significantly more
time and memory than creating a thread, as the operating system must allocate entirely new, independent memory 
spaces for each one. Destroying a process also takes time. The operating system has strict limits on how many 
processes one program can spawn. 

If too many processes are created, the system runs out of RAM, slows down drastically or crashes entirely due to 
context-switching overhead.
"""

"""
Q : What a process pool solves?
-> A process pool creates a fixed number of worker processes once at the beginning (for example, 4 or 8 workers,
usually matching the number of logical CPU cores available on the machine).

These worker processes sit idle and wait for jobs. When a new task arrives, one of the waiting processes picks
it up and immediately starts running the task function. 

When a process pool is created, no new processes are continuously spawned or destroyed during the program's
execution. This saves immense amounts of memory and CPU time, keeping the system stable under heavy loads.
"""

"""
Unlike threads, which share one Global Interpreter Lock (GIL) and cannot execute Python bytecode simultaneously,
processes bypass this limitation entirely.

Because each process spawned by the pool has its own memory space, it also possesses its own individual GIL.
Multiple tasks execute truly in parallel across multiple CPU cores. Each task is handled by its own process,
and multiple lines of Python bytecode are executed at the exact same physical time.

-> Suppose the code is like: 
filtered_image = image.apply_complex_filter()    # CPU-bound task
result = large_matrix.multiply(other_matrix)     # CPU-bound task
hash_value = calculate_sha256(large_file)        # CPU-bound task
primes = calculate_primes_up_to(10000000)        # CPU-bound task

Q : What actually happens during executing CPU-bound tasks?
-> When the code performs heavy calculations like processing high-resolution images, crunching numbers or 
parsing massive JSON files, the CPU is actively working at 100% capacity. It does not pause to wait for the 
operating system or network.

Since the CPU is constantly busy executing Python instructions, using threads would result in a bottleneck because 
the GIL forces threads to take turns. By handing these heavy tasks over to a process pool, the operating system 
assigns different physical CPU cores to different processes.

This situation is called CPU-bound — the program's speed is entirely limited by how fast the CPU can process 
instructions, making true parallelism absolute necessary.
"""

"""
Q : How Python provides a process pool?
-> Python provides a ready-made process pool in the standard library. The class name is ProcessPoolExecutor. 
ProcessPoolExecutor is a high-level API located within the concurrent.futures module. It is used to 
asynchronously execute callables (functions) using a pool of separate, independent processes.
"""
print("\nExecution Start of Process Pool Code.\n")

# Coding Example
from concurrent.futures import ProcessPoolExecutor
import time
import os

def worker(number):
    print(f"Worker process {os.getpid()} started for task {number}.")
    # Simulating heavy CPU work
    time.sleep(2)
    print(f"Worker process {os.getpid()} finished task {number}.")
    return number * 10

# The block below is strictly required for multiprocessing in Python
if __name__ == '__main__':
    # create a pool with 3 worker processes
    with ProcessPoolExecutor(max_workers=3) as pool:

        # submit 8 tasks to the pool
        submitted_futures = []
        for i in range(8):
            future_object = pool.submit(worker, i)
            submitted_futures.append(future_object)

        # wait for each task and retrieve its result
        for future_object in submitted_futures:
            result = future_object.result()     # blocks until the task finishes
            print("Result From Task : ", result)

"""
The `with` statement automatically calls shutdown(wait=True) when the block ends. This waits for all queued tasks 
to finish and then cleanly stops the worker processes. 

The max_workers argument sets the maximum number of simultaneous worker processes. If left blank, Python 
automatically defaults to the machine's processor count.

The submit method accepts a callable and its arguments, serializes (pickles) the data to send it to the worker 
process, places the task into the queue, and returns a Future object immediately. submit() does not wait for 
the task to finish. The Future object is a representation of an eventual result.

When future_object.result() is called, the calling flow pauses (blocks) until one of the following conditions is met:
1. The background task associated with the Future has completed successfully, in which case result() returns 
the value returned by the task.
2. An exception was raised during the execution of the background task, in which case result() re-raises 
that same exception in the calling flow.

Because processes do not share memory, all arguments passed to the worker function and all return values must 
be serializable (picklable). The main process and the worker processes communicate by passing serialized 
messages back and forth under the hood.
"""

"""
In a ProcessPoolExecutor, the main process and worker processes are like two different people living in two different 
houses with no shared doors. To exchange a physical object, they must pack it into a box, mail it through a delivery 
service, and unpack it at the destination. In Python, this "packing" is called Serialization (Pickling), and the 
"delivery service" is Inter-Process Communication (IPC).

-> The Full Cycle of Data Movement

Phase 1: Submission (Inside the Main Process)
When pool.submit(worker, i) is executed, the main process does not immediately run the code. Instead, it prepares a 
"Work Request."

- Creation of the Work Item: The executor creates an internal object containing the function (worker) and the argument (i).

- Serialization (Pickling): Because the worker process cannot look inside the main process’s memory to see what i is, 
the main process uses the pickle module. It converts the worker function and the value of i into a stream of raw bytes.
The main process places these serialized bytes into a Pipe or a Queue (managed by the operating system).

- The Future Object: The submit() method immediately returns a Future object to the main process. At this moment, the 
Future is empty and "pending" because the data is still traveling through the OS pipe.

Phase 2: Execution (Inside the Worker Process)
A worker process is sitting idle, constantly "listening" to the other end of the pipe.

- Receiving Bytes: The worker process detects incoming data on the pipe and pulls the raw bytes into its own private memory.

- Deserialization (Unpickling): The worker process uses the pickle module to turn those bytes back into a Python function 
object and Python data (i).

- Running the Task: Now that the worker has the function and the data in its own memory, it executes the code: 
                        result = worker(i).

- Capturing the Return: The function finishes, and the result object now exists in the worker's memory.

Phase 3: Returning the Result (Worker back to Main)
Just as the arguments had to be packed to be sent to the worker, the result must be packed to be sent back.

- Serialization of Result: The worker process takes the result object and serializes it into a new stream of bytes 
using pickle.

- The Result Pipe: The worker process pushes these bytes into the Result Queue (a different pipe leading back to the 
main process).

- Worker Goes Idle: The worker process is now finished with that specific task and waits for the next set of bytes 
from the main process.

Phase 4: Collection (Inside the Main Process)
The main process has a background thread (the "Queue Management Thread") that watches the result pipe.

- Receiving Result Bytes: The main process pulls the bytes sent by the worker out of the pipe.

- Final Deserialization: The main process unpickles the bytes to reconstruct the original Python result object.

- Setting the Future: The main process takes this reconstructed object and places it inside the Future object that was 
created in Phase 1.

- Retrieval: When the code eventually calls future_object.result(), the main process simply hands over the object it 
just unpacked.
"""

"""
-> Easiest way to run many tasks: .map()
"""
print("\nExecution Start of Process Pool Map Code.\n")

# Coding Example
if __name__ == '__main__':
    with ProcessPoolExecutor(max_workers=4) as pool:
        numbers = [1, 2, 3, 4, 5, 6, 7, 8]
        # chunksize is a special optimization argument for ProcessPoolExecutor.map
        results = pool.map(worker, numbers, chunksize=2)
        results = list(results)

    print("Result of Map Function : ", results)

"""
Q : What pool.map() actually does?
1. Tasks are grouped and submitted
 - When pool.map(worker, numbers, chunksize=2) is called, the method submits the tasks to the process pool.
 - Unlike ThreadPoolExecutor, ProcessPoolExecutor's map method accepts a 'chunksize' argument. Because passing 
   data between separate processes adds overhead (due to serialization/pickling), grouping multiple items into a single 
   chunk improves performance drastically for large datasets.
 - With max_workers=4, 8 items, and chunksize=2: The iterable is split into 4 chunks of 2 items each. These chunks 
   are distributed to the worker processes, reducing the amount of inter-process communication required.

2. It returns a generator (not a list)
 - After submission, map returns a generator.
 - At the exact moment the line results = pool.map(...) is executed:
    - The chunks have been submitted to the internal queues.
    - The generator is waiting to be iterated.

3. Results are collected strictly in order
When the returned generator is consumed (by list(), a for loop, or next()), the following happens:
 - The generator waits for the corresponding task to finish.
 - This call blocks the main program flow until that specific task finishes.
 - Once the task completes, the result is yielded.
 - Because the collection happens strictly in submission order, the yielded results always appear in the 
   same order as the input list, even if the worker processes finished the chunks in a completely different sequence.

4. Exception handling is automatic
 - If any task raises an exception, the generator raises that same exception exactly at the moment the 
   corresponding result is requested.
 - Results before the failed task are returned normally. Results after the failed task are never processed.

5. The __name__ == '__main__' requirement
 - Creating new processes involves importing the main script. If the execution code is not protected inside 
   the `if __name__ == '__main__':` block, the new worker processes will recursively attempt to create their 
   own process pools, leading to an infinite loop and an eventual crash (RuntimeError). This block ensures the 
   pool is only created once by the original parent process.
"""
