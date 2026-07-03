import asyncio
import time
from contextlib import asynccontextmanager


def download_webpage(url: str) -> str:
    print(f'[Thread] Downloading {url} (Blocking Operation)')
    time.sleep(2)   # Network Delay Simulate

    text = f"""
        <html>
            <body>
                Content of {url}
            </body>
        </html>
    """

    print(f"[Thread] Download Complete for {url}")
    return text


def update_status(url: str) -> None:
    print(f"[Thread] Updating statistics for {url} (blocking operation)...")
    time.sleep(1)   # Delay of Database Write
    print(f"[Thread] Statistics updated for {url}.")


def process(data: str) -> None:
    print(f"[Main] Processing Data : {data}")


@asynccontextmanager
async def web_page(url: str):
    loop = asyncio.get_running_loop()

    data = await loop.run_in_executor(None, download_webpage, url)

    yield data

    await loop.run_in_executor(None, update_status, url)


async def main():
    print("[Main] Starting the program...\n")

    async with web_page('aranik43.blogspot.com') as data:
        process(data)

    print("\n[Main] Program finished.")


if __name__ == '__main__':
    asyncio.run(main())

