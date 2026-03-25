"""
# Sequential Download Script
"""

import time
from pathlib import Path
from typing import Callable
import httpx

POP20_CC = 'CN IN US ID BR PK NG BD RU JP MX PH VN ET EG DE IR TR CD FR'.split()
"""
split convert string like ['CN', 'IN', 'US', 'ID', ...]
"""

BASE_URL = 'https://www.fluentpython.com/data/flags'
DEST_DIR = Path('sequential_downloaded')
"""
Creates a Path object pointing to "Desktop" folder. This is relative path.
"""

def save_flag(img: bytes, filename: str) -> None:
    (DEST_DIR / filename).write_bytes(img)

"""
-> (DEST_DIR / filename)
suppose filename is BD.gif then this joins path, Path('Desktop')/'BD.gif' → Path('Desktop/BD.gif')

-> write_bytes(img)
 - Creates the file if it does not exist.
 - Opens the file in binary write mode (wb).
 - Writes the given bytes data (img) into the file.
 - Closes the file automatically after writing.
"""

def get_flag(cc: str) -> bytes:
    url = f'{BASE_URL}/{cc}/{cc}.gif'.lower()       # url create like https://www.fluentpython.com/data/flags/bd/bd.gif
    resp = httpx.get(url, timeout=6.1, follow_redirects=True)
    resp.raise_for_status()
    return resp.content

"""
-> httpx library provide both synchronous and asynchronous APIs.

-> timeout=6.1
for Each response wait max 6.1 seconds

-> follow_redirects=True
Automatically handles HTTP redirects. Here redirects means when we request a URL, the server can respond with a redirect 
(status codes 3xx) like 301 or 302. suppose we request http://example.com but it redirects to https://example.com

if follow_redirects=True then The library automatically sends a new request to the URL in the redirect. we get the final 
content without manually handling the redirect.

-> resp
{'status_code': 200, 'headers': Headers({'date': 'Sun, 22 Mar 2026 16:55:07 GMT', 'server': 'Apache', 
'upgrade': 'h2', 'connection': 'Upgrade, Keep-Alive', 'last-modified': 'Mon, 23 Feb 2015 18:44:32 GMT', 
'etag': '"ab3-50fc5cafb6400"', 'accept-ranges': 'bytes', 'content-length': '2739', 'cache-control': 'max-age=2592000', 
'expires': 'Tue, 21 Apr 2026 16:55:07 GMT', 'vary': 'User-Agent', 'keep-alive': 'timeout=5, max=100', 
'content-type': 'image/gif'}), '_request': <Request('GET', 'https://www.fluentpython.com/data/flags/bd/bd.gif')>, 
'next_request': None, 'extensions': {'http_version': b'HTTP/1.1', 'reason_phrase': b'OK', 
'network_stream': <httpcore._backends.sync.SyncStream object at 0x105d89a90>}, 'history': [], 'is_closed': True, 
'is_stream_consumed': True, 'default_encoding': 'utf-8', 'stream': <httpx._client.BoundSyncStream object at 0x105dee270>, 
'_num_bytes_downloaded': 2739, '_decoder': <httpx._decoders.IdentityDecoder object at 0x105dee510>, 
'_elapsed': datetime.timedelta(seconds=1, microseconds=6712), '_content': b'....binary_data......'}

-> resp.raise_for_status()
if response like 404 or 500 then Raises exception.
"""

def download_many(cc_list: list[str]) -> int:
    for cc in sorted(cc_list):
        image = get_flag(cc)
        save_flag(image, f'{cc}.gif')
        print(cc, end=' ', flush=True)
    return len(cc_list)

"""
Here Callable[[list[str]], int] means, downloader is a function that takes list[str] and returns int.
"""
def main(downloader: Callable[[list[str]], int]) -> None:
    DEST_DIR.mkdir(exist_ok=True)
    t0 = time.perf_counter()
    count = downloader(POP20_CC)
    elapsed = time.perf_counter() - t0
    print(f'\n{count} downloads in {elapsed:.2f}s')


if __name__ == '__main__':
    main(download_many)
