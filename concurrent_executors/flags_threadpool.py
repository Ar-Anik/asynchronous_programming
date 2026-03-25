import time
from pathlib import Path
from typing import Callable

import httpx
from concurrent import futures

POP20_CC = 'CN IN US ID BR PK NG BD RU JP MX PH VN ET EG DE IR TR CD FR'.split()

BASE_URL = 'https://www.fluentpython.com/data/flags'
DEST_DIR = Path('threadpool_downloaded')


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
    """
        If max_workers is not specified, then max_workers = min(32, os.cpu_count() + 4)
        Below example max_workers is 12.
    """
    with futures.ThreadPoolExecutor() as executor:
        # print(executor._max_workers)
        results = executor.map(download_one, sorted(cc_list))
        # print("map : ", results.__dir__())
        return len(list(results))

"""
Part-1 :
with futures.ThreadPoolExecutor() as executor:
    results = executor.map(download_one, sorted(cc_list))
    return len(list(results))

Part-2 :
executor = ThreadPoolExecutor()
try:
    res = executor.map(download_one, sorted(cc_list))
finally:
    executor.shutdown(wait=True)

Part-1 and Part-2 are Equivalent.

Here Part-2 wait=True Parameter means, Blocks (waits) until:
 - All submitted tasks finish
 - All threads complete execution

When using ThreadPoolExecutor with a with statement, the executor automatically calls shutdown(wait=True) when finish
execute the block. This ensures that the calling thread blocks until all submitted tasks are completed, even if the 
results are not explicitly consumed (e.g., without calling list(results)).
"""

def main(downloader: Callable[[list[str]], int]) -> None:
    DEST_DIR.mkdir(exist_ok=True)

    t0 = time.perf_counter()
    count = downloader(POP20_CC)
    elapsed = time.perf_counter() - t0

    print(f'\n{count} downloads in {elapsed:.2f}s')


if __name__ == '__main__':
    main(download_many)
