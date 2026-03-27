print("\nExecution Start of Process Pool Code.\n")

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
Result : 
Execution Start of Process Pool Code.


Execution Start of Process Pool Code.


Execution Start of Process Pool Code.


Execution Start of Process Pool Code.

Worker process 4456 started for task 0.
Worker process 4457 started for task 1.
Worker process 4458 started for task 2.
Worker process 4456 finished task 0.
Worker process 4457 finished task 1.
Worker process 4456 started for task 3.
Worker process 4458 finished task 2.
Result From Task :  0
Worker process 4458 started for task 5.
Worker process 4457 started for task 4.
Result From Task :  10
Result From Task :  20
Worker process 4457 finished task 4.
Worker process 4456 finished task 3.
Worker process 4457 started for task 6.
Worker process 4458 finished task 5.
Worker process 4456 started for task 7.
Result From Task :  30
Result From Task :  40
Result From Task :  50
Worker process 4457 finished task 6.
Worker process 4456 finished task 7.
Result From Task :  60
Result From Task :  70

Here the string Execution Start of Process Pool Code. appears exactly four times in the output. This occurs because of 
how the operating system (specifically Windows and macOS) creates new processes in Python using the "spawn" start method.

When a ProcessPoolExecutor is initialized with max_workers=3, Python must create three brand-new, independent processes. 
Unlike threads, which are just sub-parts of the existing process, a spawned process is a completely fresh instance of the 
Python interpreter.

A fresh interpreter starts with an empty memory. It does not know that the worker function exists, nor does it know about 
any other variables defined in the script. To "learn" about the code it needs to run, each worker process must import the 
original script.

When a worker process starts, it effectively runs the entire script from top to bottom to load all function and class 
definitions into its own memory.

# Line 1: The worker process sees print("\nExecution Start of Process Pool Code.\n"). Since this line is at the top 
level and not inside any function or conditional block, the worker process executes it immediately.

- The Main Process: Runs the print once when the script is first started.
- Worker 1: Runs the print once when it is spawned and imports the script.
- Worker 2: Runs the print once when it is spawned and imports the script.
- Worker 3: Runs the print once when it is spawned and imports the script.

Because there is one main process and three worker processes, the top-level print statement executes a total of four times.
"""
