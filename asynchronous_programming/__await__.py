"""
Q : Cooperative Multitasking কী?
-> সাধারণ operating system-এ যখন multitasking হয় (যেমন একই সাথে গান শোনা এবং codig করা), তখন OS জোরপূর্বক একটি সফটওয়্যারকে থামিয়ে প্রসেসরের 
নিয়ন্ত্রণ অন্য সফটওয়্যারকে দিয়ে দেয়। এটিকে বলা হয় Preemptive Multitasking।

কিন্তু পাইথনের asyncio কাজ করে Cooperative Multitasking নিয়মে। এখানে
- Cooperative (সহযোগিতামূলক): এখানে কোনো Task-কে OS বা Event Loop জোর করে থামায় না। একটি Task নিজেই Event Loop-কে সহযোগিতা করে। টাস্কটি 
যখনই কোনো অলস বসে থাকার মতো কাজ (যেমন নেটওয়ার্ক রিকোয়েস্ট বা ফাইল storage অপারেশন) পায়, তখন সে নিজেই বলে, "আমার এই কাজটি শেষ হতে সময় 
লাগবে, আমি স্বেচ্ছায় control ছেড়ে দিচ্ছি (Yield করছি)। Event Loop, এই অবশরের সময়ে অন্য কোনো Task execute করো।"

- Multitasking: এই সহযোগিতার ফলেই একটিমাত্র Thread বা কোড রানার হওয়া সত্ত্বেও Event Loop একসাথে হাজার হাজার Task Maintain করতে পারে। একটি টাস্ক 
যখন ডেটার জন্য অপেক্ষা করে, Event Loop তখন অন্য টাস্কে সময় দেয়।
"""

"""
যেকোনো বাস্তবমুখী Asynchronous function বা object-এর ভেতরে কেবল একটি মাত্র await বা yield থাকে না; বরং একাধিক থাকতে পারে।

মনে করা যাক, একটি Asynchronous ফাংশনের ভেতরে 3 টি Main Step আছে:
১. Database থেকে user profile fetch করা (await / yield Point-1)
২. সেই Profile process করে হার্ডডিস্কে ফাইল হিসেবে write করা (await / yield Point-2)
৩. user-কে একটি email Confirmation পাঠানো (await / yield Point-3)

এই সম্পূর্ণ কাজটি একটি একক Iterator হিসেবে কাজ করে। Event Loop এই টাস্কটিকে একবারে শেষ করতে পারে না। একে ধাপে ধাপে এগিয়ে নিতে হয়:
Step-1: Event Loop প্রথমে Iterator-টির উপর ১ম বার send(None) command দেয়। Iterator-টি প্রথম yield পয়েন্টে (ডাটাবেজ কোয়েরি) গিয়ে pause হয়ে যায় 
এবং control লুপের কাছে ফেরত দেয়।

Step-2: ডাটাবেজের কাজ শেষ হলে Event Loop আবার ফিরে এসে ২য় বার send(None) call করে। এবার কোডটি ১ম yield থেকে যাত্রা শুরু করে ২য় yield পয়েন্টে 
(ফাইল write) গিয়ে আবার pause হয়ে যায়।

Step-3: ফাইলের কাজ শেষ হলে Event Loop ৩য় বার send(None) call করে। কোডটি তখন শেষ yield পার হয়ে চূড়ান্ত ফলাফলে পৌঁছায়।

একটি Asynchronous কাজ সম্পূর্ণ শেষ না হওয়া পর্যন্ত Event Loop পর্যায়ক্রমিকভাবে এবং ধাপে ধাপে এই মেথডগুলো call করে টাস্কটিকে সামনের দিকে এগিয়ে নিয়ে যায়।
"""

"""
Q : Awaitable Protocol কী?
পাইথনে যখন কোনো object-এর পূর্বে await key-word ব্যবহার করা হয়, তখন পাইথন সেই object-টিকে একটি Awaitable Object হিসেবে বিবেচনা করে। কোনো সাধারণ
ক্লাসকে Awaitable করে তুলতে হলে তার ভেতরে __await__ মেথডটি define করতে হয়। এটি পাইথনের একটি নির্দিষ্ট protocol।

যদি কোনো ক্লাসে এই মেথডটি না থাকে এবং সেটিকে await করার চেষ্টা করা হয়, তবে পাইথন একটি TypeError:
    object X can't be used in 'await' expression
Error প্রদর্শন করবে।
"""

"""
-> __await__ এবং Iterator এর internal relation
__await__ মেথডের একমাত্র দায়িত্ব হলো একটি iterator return করা। এই মেথডটি সরাসরি কোনো চূড়ান্ত ডেটা return করে না, বরং একটি জেনারেটর (Generator) 
বা এমন একটি custom object return করে যা __next__ এবং send() মেথড support করে।

যখন একটি await command run করা হয়, তখন ব্যাকগ্রাউন্ডে নিচের sequence-টি ঘটে:
1. system প্রথমে সংশ্লিষ্ট object-এর __await__ মেথড call করে এবং একটি iterator সংগ্রহ করে।

2. Event Loop সেই iterator-এর উপর প্রথমবার send(None) call করে। এর ফলে কোডটি চলা শুরু করে এবং প্রথম yield পয়েন্ট পর্যন্ত গিয়ে Pause হয়ে যায়।

3. yield হওয়া মাত্রই ইটারেটরটি Event লুপের কাছে control ফিরিয়ে দেয়।

4. Event loop তখন এই টাস্কটিকে pending অবস্থায় রেখে অন্য কোনো Task execute করতে চলে যায়।

5. ব্যাকগ্রাউন্ডে কাজটি শেষ হলে Event Loop আবার ফিরে আসে এবং ঐ একই iterator-এর উপর পুনরায় send(None) call করে তাকে সচল করে।

৬. যখন কাজটি সম্পূর্ণ শেষ হয়, তখন ইটারেটরটি একটি StopIteration expection raise করে। এই exception-এর সাথে মূল ফলাফল বা text যুক্ত থাকে যা 
পাইথন automatic ভাবে Extract করে ভেরিয়েবলে Assign করে।
"""

# Example

import asyncio

class CustomAsynchronousTask:
    def __init__(self, task_name):
        self.task_name = task_name
        self._fetched = False

    def __await__(self):
        # __await__ মেথডকে অবশ্যই একটি iterator রিটার্ন করতে হবে।
        # পাইথনে জেনারেটর হলো এক ধরণের iterator, তাই এখানে yield ব্যবহার করা হয়েছে।
        if not self._fetched:
            print(f"[{self.task_name}] Starting internal processing...")
            self._fetched = True

            yield
            yield

        return f"[{self.task_name}] Data fetched successfully!"

async def main():
    task = CustomAsynchronousTask('Database_Query_1')
    print("Preparing to await the task...")

    result = await task
    print(f"Result: {result}")

asyncio.run(main())

"""
পাইথনের asyncio engine-এর নিয়ম অনুযায়ী, একটি custom __await__ মেথডের ভেতরের ইটারেটর বা জেনারেটর কেবল দুটি জিনিস yield করতে পারে:
1. None (অথবা শুধু yield): যা ইভেন্ট লুপকে নির্দেশ করে যে টাস্কটি এখন pause হবে এবং পরবর্তী সাইকেলে আবার run হবে।
2. একটি Future object: যা কোনো ব্যাকগ্রাউন্ড অপারেশনের সমাপ্তির জন্য wait করতে ব্যবহৃত হয়।
"""

