"""
যদি কোনো বিশেষ কারণে একটি array বা লিস্টের data-কে async for লুপ বা __anext__() এর মাধ্যমে fetch করার প্রয়োজন হয়, তবে সেই লিস্টটিকে একটি কাস্টম ক্লাসের সাহায্যে অ্যাসিনক্রোনাস ইটারেটর বা জেনারেটরের মধ্যে রূপান্তর করতে হবে।
"""

import asyncio

class AsyncArrayWrapper:
    def __init__(self, data_list):
        self.data = data_list
        self.index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index >= len(self.data):
            raise StopAsyncIteration

        # data fetch করার মাঝে একটি custom delay তৈরি করা হলো
        await asyncio.sleep(0.5)

        result = self.data[self.index]
        self.index += 1

        return result


async def main():
    my_list = [10, 20, 30, 40, 50]

    async_iterable = AsyncArrayWrapper(my_list)

    async for each in async_iterable:
        print(f'Get Data : {each}')


if __name__ == '__main__':
    asyncio.run(main())
