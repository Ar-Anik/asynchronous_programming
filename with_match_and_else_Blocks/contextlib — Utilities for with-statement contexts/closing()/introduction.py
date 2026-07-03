"""
পাইথনে কিছু third-party object বা legacy class থাকে যেগুলোতে data বা connection বন্ধ করার জন্য একটি .close() method থাকে, কিন্তু সেগুলো
সরাসরি with statement সমর্থন করে না (অর্থাৎ তাদের ভেতরে enter এবং exit মেথড built-in থাকে না)।

contextlib.closing(class_object) মূলত ঐ অবজেক্টগুলোকে একটি wrapper এর মধ্যে নিয়ে আসে এবং একটি context manager object return করে। এর
একমাত্র কাজ হলো, with block এর কাজ স্বাভাবিকভাবে শেষ হোক কিংবা ভেতরে কোনো exception ঘটুক, ব্লক থেকে বের হওয়ার সাথে সাথেই অবজেক্টটির(class_object)
.close() method টি স্বয়ংক্রিয়ভাবে run করিয়ে দেওয়া।
"""

# internally like code
from contextlib import contextmanager

@contextmanager
def closing(thing):
    try:
        yield thing
    finally:
        thing.close()


# Code Example: Custom Network Socket Manager
from contextlib import closing

class LegacyNetworkSocket:
    def __init__(self, host):
        self.host = host
        print(f'Socket Opened For {self.host}')

    def send_data(self, message):
        print(f'Sending: {message}')

    def close(self):
        print(f"Socket for {self.host} has been explicitly closed.")

def run_network_task():
    with closing(LegacyNetworkSocket('dummyjson.com/products')) as socket:
        socket.send_data('Data Payload 1')
        print("Inside the block - task processing.")

    print("Outside the block - check if socket is closed.")

run_network_task()

"""
# Phase 1: Architecture & Internal Structure
`contextlib.closing` এটি Python এর একটি সাধারণ class যা context manager protocol (__enter__ এবং __exit__) মেনে চলে। Python 
এর standard library source code অনুযায়ী `closing` class এর আসল internal ডিজাইনটি ঠিক এইরকম:

class closing:
    def __init__(self, thing):
        # এখানে self.thing হলো LegacyNetworkSocket এর object-টি
        self.thing = thing

    def __enter__(self):
        # with ... as এর পরের variable-এ এই object-টিকেই পাঠানো হয়
        return self.thing

    def __exit__(self, exc_type, exc_val, exc_tb):
        # with block থেকে বের হওয়ার সময় Python নিশ্চিতভাবে এই method-টি run করে
        self.thing.close()
        # এখানে কোনো True return করা হয় না, তাই block-এর ভেতরের error স্বাভাবিকভাবে বাইরে চলে যায়


# Phase 2: Full Step-by-Step Runtime Execution Flow

যখন কোডে এই অংশটুকু execute হওয়া শুরু করে:
with closing(LegacyNetworkSocket("api.example.com")) as socket:
    socket.send_data("Data Payload 1")
    print("Inside the block - task processing.")

তখন memory এবং runtime লেভেলে নিচের ধাপগুলো ক্রমানুসারে সম্পন্ন হয়:

-> PART 1: Object Instantiation (The Argument Phase)
Python সবার আগে `closing()` এর ব্র্যাকেটের ভেতরের অংশটুকু execute করে। অর্থাৎ LegacyNetworkSocket("api.example.com") call হয়। class এর 
__init__ method run হয় এবং screen-এ "Socket opened for api.example.com" print হয়। এই object-টি এখন `closing` class এর 
__init__ method এর কাছে parameter হিসেবে চলে যায়।

-> PART 2: Context Manager Wrapping
Python এখন `closing` class এর একটি object(suppose it, wrapper_obj) তৈরি করে, যার ভেতরে মূল object-টি self.thing হিসেবে সংরক্ষিত থাকে।

-> PART 3: __enter__ Invocation & Target Binding
`with` block-টি শুরু হওয়া মাত্রই Python internally তৈরি হওয়া object এর __enter__() method-টিকে call করে। `closing` class এর __enter__ 
method-টি তার নিজের ভেতরের সংরক্ষিত object-টিকে (self.thing) সরাসরি return করে দেয়। Python সেই return হওয়া object-টিকে `as socket` 
অংশের socket variable এর সাথে যুক্ত করে দেয়।

-> PART 4: Block Body Execution
এবার control `with` block এর ভেতরে প্রবেশ করে এবং ভেতরের কোডগুলো একে একে execute হয়:

socket.send_data("Data Payload 1")              # "Sending: Data Payload 1" print হয়
print("Inside the block - task processing.")    # এই লাইনটি print হয়

-> PART 5: Block Exit & __exit__ Invocation
block এর ভেতরের শেষ লাইন execute হওয়া মাত্রই Python `with` block থেকে বের হওয়ার জন্য internally object এর __exit__ method-টিকে call করে।
Internal Call (কোনো error না থাকলে):
        wrapper_obj.__exit__(None, None, None)   # তিনটি parameter-ই (type, value, traceback) None হিসেবে পাস হয়

Internal Call (যদি block-এর ভেতরে কোনো error বা exception ঘটে):
        wrapper_obj.__exit__(exc_type, exc_value, exc_traceback)   # block-এর ভেতরে error ঘটলে Python internally এই parameter-গুলো পাস করে

-> PART 6: Explicit `.close()` Execution
__exit__ method এর ভেতরে প্রবেশ করার পর, Python এর লিখে রাখা internal logic অনুযায়ী সেখানে থাকা `self.thing.close()` লাইনটি trigger হয়।
এর ফলে মূল object এর নিজস্ব `close()` method-টি call হয় এবং screen-এ print হয়, "Socket for api.example.com has been explicitly closed."

-> PART 7: Final Program Continuation
__exit__ method এর কাজ শেষ হওয়ার পর control `with` block থেকে সম্পূর্ণ বাইরে চলে আসে এবং এর পরের সাধারণ কোডটি run করে:
            print("Outside the block - check if socket is closed.")
"""
