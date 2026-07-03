"""
Q : "Pyramid of Doom" কী এবং সমস্যাটি কেন ঘটে?
অ্যাসিনক্রোনাস প্রোগ্রামিংয়ে যখন কোনো টাস্ক ব্যাকগ্রাউন্ডে সম্পন্ন করার জন্য পাঠানো হয়, তখন প্রাক-আধুনিক পদ্ধতিতে (যেমন পুরানো জাভাস্ক্রিপ্ট বা পাইথনের কিছু পুরানো লাইব্রেরিতে) কলব্যাক (Callback) ফাংশন ব্যবহার করা হতো। কলব্যাক হলো এমন একটি ফাংশন, যা মূল টাস্কটি শেষ হওয়ার পর স্বয়ংক্রিয়ভাবে (automatic) রান করার জন্য পাস করা হয়।

সমস্যা তখন সৃষ্টি হয়, যখন একাধিক অ্যাসিনক্রোনাস টাস্ক একটির পর আরেকটি ক্রমানুসারে (sequence অনুযায়ী) সম্পাদন করতে হয় এবং প্রতিটি পরবর্তী টাস্ক তার পূর্ববর্তী টাস্কের ফলাফলের ওপর নির্ভর করে। এর ফলে একটি কলব্যাকের ভেতরে আরেকটি কলব্যাক, তার ভেতরে আরও একটি কলব্যাক—এভাবে কোড লিখতে হয়।

এর ফলে কোডের লেভেল বা ইনডেন্টেশন (Indentation) ডানদিকে অগ্রসর হতে হতে একটি উল্টানো পিরামিডের মতো আকৃতি ধারণ করে। একেই "Pyramid of Doom" বা "Callback Hell" বলা হয়।

এই মেথডের প্রধান সমস্যাসমূহ:
পঠনযোগ্যতা (Readability) বিনষ্ট হওয়া: কোড কোন দিক থেকে কোন দিকে প্রবাহিত হচ্ছে তা ট্র্যাক করা কঠিন হয়ে পড়ে।

জটিল এরর হ্যান্ডলিং: সাধারণ try/except ব্লক দিয়ে এই ধরনের নেস্টেড কলব্যাকের ভেতরের এরর ক্যাচ করা যায় না। প্রতিটি লেভেলে আলাদা আলাদা এরর হ্যান্ডলিং logic check করতে হয়।

রক্ষণাবেক্ষণের অসুবিধা (Maintainability): কোডের কোনো অংশে পরিবর্তন বা নতুন কোনো ফিচার যুক্ত করতে গেলে পুরো আর্কিটেকচার ভেঙে পড়ার ঝুঁকি থাকে।

২. পাইথনে কোড উদাহরণ: প্রথাগত কলব্যাক পদ্ধতি (The Problem)
বোঝার সুবিধার জন্য নিচে একটি বাস্তবসম্মত সিনারিও তৈরি করা হলো:
১. প্রথমে ইউজার আইডি দিয়ে ইউজারের তথ্য আনা হবে।
২. সেই তথ্যের ওপর ভিত্তি করে ইউজারের পোস্টসমূহ লোড করা হবে।
৩. সবশেষে সেই পোস্টগুলোকে লোকাল মেমোরিতে সেভ করা হবে।

নিচের পাইথন কোডটি লক্ষ্য করলে দেখা যাবে কীভাবে সাধারণ ফাংশন এবং কলব্যাক ব্যবহারের কারণে একটি coding পিরামিড তৈরি হয়েছে:
"""

def fetch_user_data(user_id, callback):
    print(f'Fetching User Data For ID : {user_id}')
    user_object = {'id': user_id, 'name': 'Anik'}

    callback(user_object)


def fetch_user_posts(user_object, callback):
    print(f'Fetching Posts For User : {user_object['name']}')
    posts_list = ['Post-1', 'Post-2', 'Post-3']

    callback(posts_list)


def save_posts_to_cache(posts_listt, callback):
    print('Saving Posts to cache storage....')
    status_text = "Success"

    callback(status_text)

def main_process():
    fetch_user_data(101, lambda user:
        fetch_user_posts(user, lambda posts:
            save_posts_to_cache(posts, lambda status:
                print(f"Final Execution Status: {status_text if 'status_text' in locals() else status}")
            )
        )
    )

if __name__ == '__main__':
    main_process()

"""
উপরের কোডে main_process-এর ভেতরের অংশটি লক্ষ্য করলে দেখা যাবে যে, কোডটি ক্রমশ ডানদিকে বেঁকে যাচ্ছে। যদি এখানে ১০টি এই ধরনের ক্রমানুসারী টাস্ক থাকতো, তবে কোডটি স্ক্রিনের বাইরে চলে যেত এবং এরর হ্যান্ডলিং করার জন্য প্রতিটি ল্যাম্বডা (lambda) ফাংশনের ভেতরে আলাদা logic check বসাতে হতো, যা কোডকে আরও নোংরা করে তোলে।

-> async এবং await কীভাবে এই জটিলতা দূর করে?
async এবং await কিউওয়ার্ডের আবিষ্কার অ্যাসিনক্রোনাস কোড লেখার ধরন সম্পূর্ণ বদলে দিয়েছে। এটি ব্যাকগ্রাউন্ডে অ্যাসিনক্রোনাস মেকানিজম বজায় রেখেই কোডকে সাধারণ সিনক্রোনাস (Synchronous) বা লাইনার কোডের মতো দেখানোর সুবিধা দেয়।

যখন কোনো ফাংশনের সামনে await ব্যবহার করা হয়, তখন system-এর ইভেন্ট লুপকে নির্দেশ দেওয়া হয়: "এই নির্দিষ্ট টাস্কটি শেষ না হওয়া পর্যন্ত বর্তমান ফাংশনের execution সাময়িকভাবে স্থগিত রাখো, এবং এই ফাঁকে অন্য কোনো টাস্ক থাকলে তা সম্পন্ন করো।"

টাস্কটি শেষ হওয়া মাত্রই কোডটি কোনো কলব্যাক ফাংশন ছাড়াই ঠিক তার পরের লাইন থেকে পুনরায় রান করা শুরু করে। এর ফলে পিরামিড কাঠামোটি ভেঙে সম্পূর্ণ সোজা এবং সমান্তরাল লাইনে পরিণত হয়।

নিচে একই কাজের আধুনিক এবং পরিচ্ছন্ন রূপ দেখানো হলো, যেখানে asyncio মডিউল ব্যবহার করে সম্পূর্ণ পিরামিড কাঠামো দূর করা হয়েছে:
"""

import asyncio

async def fetch_user_data(user_id):
    print(f"Fetching user data for ID: {user_id}")
    await asyncio.sleep(1)

    return {'id': user_id, 'name': 'Aubdur Rob Anik'}

async def fetch_user_posts(user_object):
    print(f'Fetching Posts For User: {user_object['name']}')
    await asyncio.sleep(1)

    return ['Post-1', 'Post-2', 'Post-3']

async def save_posts_to_cache(posts_list):
    print("Saving posts to cache storage...")
    await asyncio.sleep(1)

    return 'Success'

async def main_process():
    try:
        user = await fetch_user_data(101)
        posts = await fetch_user_posts(user)
        status = await save_posts_to_cache(posts)

        print(f'Final Execution Status : {status}')

    except Exception as exc:
        print(f"An error occurred during execute: {exc}")

if __name__ == '__main__':
    asyncio.run(main_process())

"""
- কোডটি উপর থেকে নিচে অত্যন্ত সহজভাবে পড়া যাচ্ছে। কোনো ফাংশনের ভেতরে অন্য ফাংশন পাস করতে হচ্ছে না।
- প্রথাগত পাইথন কোডের মতোই স্ট্যান্ডার্ড try/except ব্লক ব্যবহার করে পুরো সিক্যুয়েন্সের যেকোনো লাইনের এরর এক জায়গায় ক্যাচ করা যাচ্ছে।
- মাঝখানে যদি নতুন কোনো ভ্যালিডেশন বা ডাটা প্রসেসিং মেথড যুক্ত করার প্রয়োজন হয়, তবে শুধুমাত্র একটি নতুন লাইন লিখে তার আগে await বসিয়ে দিলেই কাজ সম্পন্ন হয়। কোডের অন্য কোনো কাঠামো পরিবর্তন করার প্রয়োজন পড়ে না।
"""
