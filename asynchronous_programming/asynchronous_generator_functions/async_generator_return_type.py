"""
যখন একটি Asynchronous Generator function (যা async def দিয়ে শুরু হয় এবং ভেতরে yield থাকে) call করা হয়, তখন এটি ভেতরের কোড সাথে সাথে রান করে না। এটি তাৎক্ষণিকভাবে একটি Asynchronous Generator Object return করে।
"""

async def async_generator():
    yield 1
    yield 2

gen_obj = async_generator()
print(gen_obj)

"""
Asynchronous Generator-এর ভেতরে return keyword ব্যবহার করা সম্ভব। তবে সাধারণ generator-এর সাথে এর একটি প্রধান পার্থক্য রয়েছে।
- সাধারণ Generator: কোডের ভেতরে return "value" লিখলে সেই ভ্যালুটি StopIteration exception-এর সাথে যুক্ত হয়ে ফেরত যায়।
- Asynchronous Generator: এর ভেতরে return-এর পর কোনো ভ্যালু (যেমন: return "done") লেখা যায় না। ভ্যালুসহ লিখলে Python একটি SyntaxError দেখাবে। এটি শুধুমাত্র খালি return সমর্থন করে।

যখন Asynchronous Generator-এর ভেতরে একটি খালি return পাওয়া যায়, তখন যা হয়:
- Termination: জেনারেটরের execution সেখানেই শেষ হয়ে যায়।
- Exception Triggered: async for loop শেষ করার জন্য background-এ একটি StopAsyncIteration exception তৈরি হয়।
"""
import asyncio
async def limited_async_gen():
    yield "First Date"
    yield "Second Data"
    return
    yield "Third Data"

async def main():
    async for item in limited_async_gen():
        print(item)

asyncio.run(main())

"""
Normal Generator Vs Asynchronous Generator-এর Return পার্থক্য (Note Format)

-> Normal Generator:
- Function call করলে এটি একটি Generator Object return করে।
- এর ভেতরে value সহ return (return "value") করা সম্ভব।
- Loop শেষ হলে এটি StopIteration exception তৈরি করে এবং value-টি সেই exception-এর সাথে যুক্ত থাকে।

-> Asynchronous Generator:
- Function call করলে এটি একটি Asynchronous Generator Object return করে।
- এর ভেতরে value সহ return করা অসম্ভব, শুধুমাত্র খালি return লেখা যাবে। Value দিলে SyntaxError: 'return' with value in async generator দেখাবে।
- Loop শেষ হলে এটি StopAsyncIteration exception তৈরি করে।
"""
