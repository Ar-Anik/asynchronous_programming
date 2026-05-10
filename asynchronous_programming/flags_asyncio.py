#!/usr/bin/env python3

"""Download flags of top 20 countries by population

asyncio + aiottp version

Sample run::

    $ python3 flags_asyncio.py
    EG VN IN TR RU ID US DE CN MX JP BD NG ET FR BR PH PK CD IR
    20 flags downloaded in 1.07s
"""
# tag::FLAGS_ASYNCIO_TOP[]
import time
import asyncio
from pathlib import Path
from typing import Callable
from httpx import AsyncClient  # <1>

POP20_CC = 'CN IN US ID BR PK NG BD RU JP MX PH VN ET EG DE IR TR CD FR'.split()

BASE_URL = 'https://www.fluentpython.com/data/flags'
DEST_DIR = Path('asynchronously_downloaded_flag')

def save_flag(img: bytes, filename:str) -> None:
    (DEST_DIR/filename).write_bytes(img)


async def download_one(client: AsyncClient, cc: str):  # <3>
    image = await get_flag(client, cc)
    save_flag(image, f'{cc}.gif')
    print(cc, end=' ', flush=True)
    return cc


async def get_flag(client: AsyncClient, cc: str) -> bytes:  # <4>
    url = f'{BASE_URL}/{cc}/{cc}.gif'.lower()
    resp = await client.get(url, timeout=6.1, follow_redirects=True)  # <5>
    return resp.read()  # <6>

# end::FLAGS_ASYNCIO_TOP[]

# tag::FLAGS_ASYNCIO_START[]
def download_many(cc_list: list[str]) -> int:    # <1>
    return asyncio.run(supervisor(cc_list))      # <2>


async def supervisor(cc_list: list[str]) -> int:
    async with AsyncClient() as client:          # <3>
        to_do = [download_one(client, cc)
                 for cc in sorted(cc_list)]      # <4>
        res = await asyncio.gather(*to_do)       # <5>

    return len(res)                              # <6>


def main(downloader: Callable[[list[str]], int]) -> None:
    DEST_DIR.mkdir(exist_ok=True)
    t0 = time.perf_counter()
    count = downloader(POP20_CC)
    elapsed = time.perf_counter() - t0
    print(f'\n{count} downloads in {elapsed:.2f}s')


if __name__ == '__main__':
    main(download_many)

# end::FLAGS_ASYNCIO_START[]
