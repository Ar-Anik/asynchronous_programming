"""
Future in both concurrent.futures and asyncio represents the result of a task that will be available later. It provides a
way to track the execution of that task. The .done() method is non-blocking, meaning it does not wait for the task to
finish; instead, it immediately returns a Boolean value indicating whether the task has completed (True) or is still
running (False). However, repeatedly calling .done() to check completion (polling) is inefficient and not recommended.

Instead of polling, Futures provide the .add_done_callback() method, which allows registering a callable (callback
function). This callback is automatically executed once the task finishes, and it receives the Future object as its
only argument, allowing access to the result via methods like .result(). An important detail is that the callback runs
in the same execution context as the task: in a worker thread for ThreadPoolExecutor, in a worker process for
ProcessPoolExecutor, and in the event loop thread for asyncio.Future.
"""

import time
from concurrent.futures import ThreadPoolExecutor
import threading


def task_function(n):
    print(f"Task started: {n} (Thread: {threading.current_thread().name})")
    time.sleep(2)
    return n * n


# This is the callback function that will be triggered when the task is done
def callback_function(future):
    # The Future object is passed as an argument
    result = future.result()
    print(f"\nCallback triggered!")
    print(f"Result: {result} (Thread: {threading.current_thread().name})")


def main():
    with ThreadPoolExecutor(max_workers=1) as executor:
        print("Submitting task...")

        future = executor.submit(task_function, 5)

        # Register the callback using .add_done_callback()
        future.add_done_callback(callback_function)

        print("Main thread is doing other work...")
        for i in range(3):
            print(f"Main thread count: {i}")
            time.sleep(1)


if __name__ == "__main__":
    main()
