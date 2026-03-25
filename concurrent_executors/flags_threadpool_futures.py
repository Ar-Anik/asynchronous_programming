import time
from pathlib import Path
from typing import Callable

import httpx
from concurrent.futures import ThreadPoolExecutor, Future, as_completed

POP20_CC = 'CN IN US ID BR PK NG BD RU JP MX PH VN ET EG DE IR TR CD FR'.split()

BASE_URL = 'https://www.fluentpython.com/data/flags'
DEST_DIR = Path('threadpool_future_downloaded')


def save_flag(img: bytes, filename: str) -> None:
    (DEST_DIR / filename).write_bytes(img)


def get_flag(cc: str) -> bytes:
    url = f'{BASE_URL}/{cc}/{cc}.gif'.lower()
    resp = httpx.get(url, timeout=6.1, follow_redirects=True)
    resp.raise_for_status()
    return resp.content


def download_one(cc: str) -> str:
    image = get_flag(cc)
    save_flag(image, f'{cc}.gif')
    print(cc, end=' ', flush=True)
    return cc

def download_many(cc_list: list[str]) -> int:
    cc_list = cc_list[:5]

    with ThreadPoolExecutor(max_workers=3) as executor:
        to_do: list[Future] = []
        for cc in sorted(cc_list):
            future = executor.submit(download_one, cc)
            to_do.append(future)
            print(f'Scheduled for {cc}: {future}')

        for count, future in enumerate(as_completed(to_do), 1):
            res: str = future.result()
            print(f'{future} result: {res!r}')

    return count

def main(downloader: Callable[[list[str]], int]) -> None:
    DEST_DIR.mkdir(exist_ok=True)

    t0 = time.perf_counter()
    count = downloader(POP20_CC)
    elapsed = time.perf_counter() - t0

    print(f'\n{count} downloads in {elapsed:.2f}s')


if __name__ == '__main__':
    main(download_many)

"""
-> The Core Purpose of as_completed
When managing multiple concurrent tasks using a ThreadPoolExecutor or ProcessPoolExecutor, there are two primary ways to handle results:
1. Sequential Processing (executor.map): This returns results in the exact order the tasks were submitted. If the first 
task takes 10 seconds and the second takes 1 second, the program must wait 10 seconds before seeing any output.

2. Completion-Based Processing (as_completed): This returns the Future objects as soon as the associated callable finishes. 
If the second task finishes first, it is yielded immediately, even if the first task is still running.

-> The as_completed function takes an iterable of Future objects (the to_do list in the provided code) and returns an 
iterator. To understand the deep logic, the following internal states of a Future must be considered:
- PENDING: The task is scheduled but has not started.
- RUNNING: The task is currently being executed by a worker thread/process.
- CANCELLED: The task was removed from the queue before execution.
- FINISHED: The task has completed (either successfully or by raising an exception).

-> When as_completed(to_do) is called, the function enters a loop that monitors the state of every Future in the 
collection. It uses a internal "condition variable" or "waiter" mechanism. Instead of constantly polling each future 
(which would waste CPU cycles), the iterator "sleeps" and is "woken up" by the executor as soon as any future 
transitions to the FINISHED state.
- Yielding: The moment a future finishes, the iterator yields that specific Future object to the for loop.
- Order: The order of yielding is strictly non-deterministic. It depends entirely on network latency, OS scheduling, 
and task complexity.
- Efficiency: This approach is highly efficient for I/O-bound tasks (like downloading flags) because it prevents the 
"head-of-line blocking" problem.

-> In the above code `as_completed` is used within the download_many function.

- Stage A: Scheduling
    for cc in sorted(cc_list):
        future = executor.submit(download_one, cc)
        to_do.append(future)
The executor.submit method is non-blocking. it immediately returns a Future object representing a promise of a result. 
At this point, the to_do list contains several Future objects, most of which are likely in a PENDING or RUNNING state.

- Stage B: The as_completed Loop
    for count, future in enumerate(as_completed(to_do), 1):
        res: str = future.result()

• Block and Wait: The for loop asks as_completed for the next finished item. If no tasks are done, the loop pauses (blocks).
• Immediate Retrieval: As soon as task finishes for any Future, as_completed yields that Future.
• Result Extraction: The .result() method is called on the yielded Future. Since the iterator only yields finished 
futures, .result() will return the value immediately without further waiting.
"""
