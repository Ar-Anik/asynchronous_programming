"""
Python asyncio লাইব্রেরিতে asyncio.gather() হলো একটি অত্যন্ত শক্তিশালী এবং গুরুত্বপূর্ণ ফাংশন, যা একাধিক coroutine বা task কে একই সাথে (concurrently) 
চালানোর জন্য ব্যবহৃত হয়। 

Q : asyncio.gather() কী?
-> asyncio.gather() হলো একটি high-level API যা একাধিক awaitable অবজেক্টকে (যেমন: coroutine, task বা future) একটি group হিসেবে গ্রহণ করে 
এবং সেগুলোকে concurrently run করে। এটি সবশেষে একটি একক future return করে যেখানে প্রতিটি task এর ফলাফল একটি list হিসেবে জমা থাকে।

asyncio.gather() এর কাজের প্রক্রিয়াটি কয়েকটি ধাপে বিভক্ত:

Step-1 : Task Registration
যখন asyncio.gather(*to_do) Call করা হয়, তখন এটি তালিকার প্রতিটি coroutine কে event loop-এ রেজিস্টার করে। যদি ইনপুট হিসেবে সরাসরি coroutine
দেওয়া হয়, তবে gather() সেগুলোকে স্বয়ংক্রিয়ভাবে asyncio.Task এ রূপান্তর করে নেয় যাতে সেগুলো run করার জন্য প্রস্তুত হয়।

Step-2 : Concurrent Execution
এটি সবকটি Task কে প্রায় একই সময়ে শুরু করে। এটি কিন্তু Multi-Threading নয়; বরং এটি cooperative multitasking ব্যবহার করে। যখন একটি task কোনো
I/O অপারেশনের জন্য (যেমন: network request বা file read) await করে, তখন event loop সেই টাস্কটিকে সাময়িকভাবে থামিয়ে পরবর্তী টাস্কটি শুরু করে।

Step-3 : Result Collection
সবগুলো task সম্পন্ন না হওয়া পর্যন্ত gather() অপেক্ষা করে। Task গুলো যে ক্রমানুসারে (order) শুরু করা হয়েছিল, তাদের ফলাফলগুলো ঠিক সেই একই ক্রমানুসারে একটি
তালিকায় সাজানো থাকে, যদিও Task গুলো শেষ হওয়ার সময় আলাদা হতে পারে।

-> asyncio.gather() এর Main features
- অর্ডার বজায় রাখা (Ordering): যদি [task_a, task_b, task_c] input দেওয়া হয়, তবে ফলাফলের তালিকায় [result_a, result_b, result_c] থাকবে
এমনকি যদি task_c সবার আগে শেষ হয় তবুও।

- Error Handling: এতে return_exceptions নামে একটি প্যারামিটার থাকে।
    1. যদি return_exceptions=False (default) থাকে, তবে কোনো একটি টাস্কে error হলে পুরো gather() সেখানেই Exception throw করবে।
    2. যদি return_exceptions=True থাকে, তবে error হওয়া টাস্কটির পরিবর্তে তালিকায় সেই error অবজেক্টটি জমা থাকবে এবং বাকি টাস্কগুলো স্বাভাবিকভাবে চলবে।


- Multiple Group : এটি একসাথে বিভিন্ন ধরণের Task-এর Group Manage করতে পারে।

"""

import asyncio

async def call_api(name, delay):
    print(f'{name} Started...')
    await asyncio.sleep(delay)
    print(f'{name} finished.')
    return f'Data from {name}'

async def main():
    # Gathering three tasks to run concurrently
    results = await asyncio.gather(
        call_api('Task-1', 3),
        call_api('Task-2', 1),
        call_api('Task-3', 2)
    )

    print(f'Result List: {results}')

if __name__ == '__main__':
    asyncio.run(main())

"""
1. Task 1 শুরু হবে এবং 3 সেকেন্ডের জন্য Pause হবে।
2. সাথে সাথে Task 2 শুরু হবে এবং 1 সেকেন্ডের জন্য Pause হবে।
3. সাথে সাথে Task 3 শুরু হবে এবং ২ সেকেন্ডের জন্য Pause হবে।
4. 1 সেকেন্ড পর Task 2 শেষ হবে, 2 সেকেন্ড পর Task 3 এবং 3 সেকেন্ড পর Task 1 শেষ হবে।
5. কিন্তু results তালিকায় Data থাকবে: ['Data from Task-1', 'Data from Task-2', 'Data from Task-3']।

সাধারণ লুপ ব্যবহার করলে প্রতিটি কাজের জন্য আলাদাভাবে অপেক্ষা করতে হতো। Suppose 10 টি API Call করতে হবে এবং প্রতিটি 1 সেকেন্ড সময় নেয়। loop ব্যবহার 
করলে মোট সময় লাগবে 10 সেকেন্ড। asyncio.gather() ব্যবহার করলে, মোট সময় লাগবে মাত্র 1 সেকেন্ড (সবচেয়ে দীর্ঘতম কাজের সমান সময়)।

এটি Processor resources সাশ্রয় করে এবং network বা I/O bound অ্যাপ্লিকেশনের Performance বহুগুণ বাড়িয়ে দেয়।
"""
