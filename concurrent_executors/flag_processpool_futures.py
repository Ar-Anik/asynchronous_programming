import time
from pathlib import Path
from typing import Callable

import httpx
from concurrent.futures import ProcessPoolExecutor, Future

POP20_CC = 'CN IN US ID BR PK NG BD RU JP MX PH VN ET EG DE IR TR CD FR'.split()

BASE_URL = 'https://www.fluentpython.com/data/flags'
DEST_DIR = Path('processpool_future_downloaded')


def save_flag(img: bytes, filename:str) -> None:
    (DEST_DIR/filename).write_bytes(img)


def get_flag(cc:str) -> bytes:
    url = f'{BASE_URL}/{cc}/{cc}.gif'.lower()
    resp = httpx.get(url, timeout=6, follow_redirects=True)
    resp.raise_for_status()
    return resp.content


def download_one(cc: str) -> str:
    image = get_flag(cc)
    save_flag(image, f'{cc}.gif')
    print(cc, end=' ', flush=True)
    return cc


def download_many(cc_list: list[str]) -> int:
    with ProcessPoolExecutor(max_workers=3) as executor:
        results = executor.map(download_one, sorted(cc_list))
        return len(list(results))


def main(downloader: Callable[[list[str]], int]) -> None:
    DEST_DIR.mkdir(exist_ok=True)

    t0 = time.perf_counter()
    count = downloader(POP20_CC)
    elapsed = time.perf_counter() - t0

    print(f'\n{count} downloads in {elapsed:.2f}s')


if __name__ == '__main__':
    main(download_many)

"""
it take 2-3 extra time from threadpool.
"""
