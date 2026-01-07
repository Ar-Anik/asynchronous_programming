"""
Python-এর multiprocessing প্যাকেজ থ্রেডের পরিবর্তে আলাদা প্রসেস ব্যবহার করে একই সময়ে একাধিক কাজ (Concurrent tasks) করার সুবিধা দেয়।
যখন একটি multiprocessing.Process ইন্সট্যান্স তৈরি করা হয় তখন ব্যাকগ্রাউন্ডে চাইল্ড প্রসেস হিসেবে একটি সম্পূর্ণ নতুন পাইথন ইন্টারপ্রিটার চালু হয়।
যেহেতু প্রতিটি পাইথন প্রসেসের নিজস্ব GIL (Global Interpreter Lock) থাকে তাই এটি প্রোগ্রামের কার্যক্ষমতা বাড়াতে কম্পিউটারের সবকটি CPU কোর
ব্যবহার করতে পারে যদিও এটি শেষ পর্যন্ত অপারেটিং সিস্টেমের শিডিউলারের ওপর নির্ভর করে।
"""

import itertools
import time
from multiprocessing import Process, Event
from multiprocessing import synchronize

def spin(msg: str, done: synchronize.Event):
    for char in itertools.cycle(r'\|/-'):
        status = f'\r{char} {msg}'
        print(status, end='', flush=True)

        if done.wait(.1):
            break

    blanks = ' ' * len(status)
    print(f'\r{blanks}\r', end='')

def slow():
    time.sleep(3)
    return 42

def supervisor():
    done = Event()

    spinner = Process(target=spin, args=('thinking!', done))
    print(f'Spinner Object: {spinner}')

    spinner.start()

    result = slow()

    done.set()

    spinner.join()

    return result


def main():
    result = supervisor()
    print(f'Answer : {result}')

if __name__ == '__main__':
    main()

"""
1. Type Hinting: multiprocessing.Event আসলে একটি ফাংশন (এটি threading.Event-এর মতো সরাসরি কোনো ক্লাস নয়)। এই ফাংশনটি 
একটি synchronize.Event ইন্সট্যান্স রিটার্ন করে। একারণেই Type Hinting ব্যবহার করার জন্য আমাদের multiprocessing.synchronize ইমপোর্ট করতে হয়।

2. Process ID: যখন স্পিনার অবজেক্টটি প্রিন্ট করা হয় তখন এটি <Process(Process-1, started)> হিসেবে দেখায়। এখানে পাইথন ইন্টারপ্রিটারের একটি 
নিজস্ব Process ID (PID) থাকে।

3. Memory Isolation: থ্রেড এবং প্রসেসের মধ্যে বড় পার্থক্য হলো প্রসেসগুলো অপারেটিং সিস্টেম দ্বারা একে অপরের থেকে আলাদা থাকে। এরা সরাসরি পাইথন 
অবজেক্ট শেয়ার করতে পারে না।

4. Serialization: এক প্রসেস থেকে অন্য প্রসেসে ডেটা পাঠানোর জন্য অবজেক্টগুলোকে Serialize (Pickling) এবং Deserialize করতে হয় যা কিছুটা 
বাড়তি সময়ের (Overhead) প্রয়োজন হয়। উপরের উদাহরণে শুধুমাত্র Event স্টেটটি প্রসেসের সীমানা অতিক্রম করে যা মূলত C code দ্বারা নিয়ন্ত্রিত 
একটি low-level OS Semaphore দিয়ে তৈরি।
"""

"""
threading এবং multiprocessing-এর বেসিক API বা কাজ করার ধরন দেখতে একই রকম হলেও এদের অভ্যন্তরীণ গঠন বা ইমপ্লিমেন্টেশন সম্পূর্ণ আলাদা। 
মাল্টিপ্রসেস প্রোগ্রামিংয়ের জটিলতাগুলো সামলানোর জন্য multiprocessing-এ অনেক বড় এবং বিস্তারিত API রয়েছে।

Example :  থ্রেড থেকে প্রসেসে রূপান্তর করার সময় একটি বড় চ্যালেঞ্জ হলো প্রসেসগুলোর মধ্যে যোগাযোগ করা। যেহেতু অপারেটিং সিস্টেম প্রতিটি প্রসেসকে একে 
অপরের থেকে আলাদা বা Isolated রাখে তাই তারা সরাসরি পাইথন অবজেক্ট শেয়ার করতে পারে না। এর মানে হলো এক প্রসেসের সীমানা পার হয়ে অন্য 
প্রসেসে ডেটা পাঠাতে হলে সেই অবজেক্টগুলোকে অবশ্যই Serialize (পঠনযোগ্য ফরম্যাটে রূপান্তর) এবং পুনরায় Deserialize করতে হয় যা সিস্টেমে বাড়তি চাপ 
বা ওভারহেড (Overhead) তৈরি করে। উপরের উদাহরণে প্রসেসের সীমানা পার হওয়া একমাত্র ডেটা হলো Event state (ইভেন্টের অবস্থা)। এটি 
multiprocessing মডিউলের নিচে থাকা C code এবং low-level OS Semaphore দিয়ে তৈরি করা হয়েছে।
"""
