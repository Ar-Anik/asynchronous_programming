"""
contextmanager দিয়ে তৈরি করা function গুলোকে একই সাথে with statement এ এবং অন্য কোনো function এর উপরে decorator হিসেবে ব্যবহার করা যায়
"""

import time
from contextlib import contextmanager

@contextmanager
def execution_timer(label):
    start_time = time.monotonic()
    try:
        yield
    finally:
        end_time = time.monotonic()
        duration = end_time - start_time
        print(f"[{label}] Process took {duration:.4f} seconds.")

# Pattern-1
with execution_timer('Loop Activity'):
    total = 0
    for i in range(1_000_000):
        total += i

@execution_timer("Function Activity")
def complex_calculation():
    time.sleep(0.5)
    print("Calculation inside the decorated function is complete.")

complex_calculation()

"""
Pattern 1: এখানে এটি প্রথাগত নিয়মে with block এর কোডটুকুর শুরু এবং শেষের সময় রেকর্ড করে তার different হিসেব করে output দেয়।

Pattern 2: এখানে আলাদা কোনো with না লিখে সরাসরি function এর উপরে decorator হিসেবে @execution_timer বসিয়ে দেওয়া হয়েছে। এর ফলে প্রতিবার 
complex_calculation() function টি call করার সময় backend এ স্বয়ংক্রিয়ভাবে একটি নতুন generator instance তৈরি হবে এবং পুরো function টি execute 
হতে কত সময় লাগলো তা print করবে।
"""




"""----------------------Deep-Dive Execution Flow of @contextmanager----------------------"""
"""
Phase 1: Initialization & Decoration (Compilation Time)

PART 1: The Generator Function Discovery
def execution_timer(label):
    start_time = time.monotonic()
    try:
        yield
    finally:
        ...

ফাংশনটির ভেতরে yield keyword থাকার কারণে python compiler এটিকে সাধারণ function হিসেবে treat করে না। এটি একটি generator function হিসেবে 
মেমোরিতে registered হয়।


PART 2: @contextmanager Applied

@contextmanager
def execution_timer(label):

Behind the Scenes, এই লাইনটি Original generator ফাংশনটির উপর Decorator Apply করে। এটি internally নিচের কাজটি সম্পন্ন করে:
            execution_timer = contextmanager(execution_timer)


PART 3: contextmanager() Internal Function

contextmanager ফাংশনটির Internal architecture :
def contextmanager(func):
    def helper(*args, **kwargs):
        return _GeneratorContextManager(func, args, kwargs)
    return helper

Original Generator ফাংশনটি এখন একটি সাধারণ helper function দ্বারা replace হয়ে গেছে।

PART 4: Factory Invocation

temp = execution_timer("Function Activity")

এই লাইনটি execute হওয়া মানে মূলত helper("Function Activity") run হওয়া। এটি ব্যাকগ্রাউন্ডে _GeneratorContextManager ক্লাসের একটি object তৈরি করে 
temp ভেরিয়েবলে return করে।

PART 5: The ContextDecorator Inheritance
পাইথনের internal _GeneratorContextManager ক্লাসটি মূলত ContextDecorator ক্লাসকে inherit করে। এই ContextDecorator ক্লাসের ভেতরে __call__ 
মেথডটি তৈরি করা থাকে। এই কারণে এই অবজেক্টটি একটি callable object-এ পরিণত হয়।

PART 6: Decorator Application

@execution_timer("Function Activity")
def complex_calculation():
    ...

Behind the Scenes, python internally এই Decorator প্যাটার্নটিকে নিচের লাইনে রূপান্তর করে নেয়:
        complex_calculation = temp(complex_calculation)

PART 7: __call__ Method Invocation
পাইথনে কোনো অবজেক্টের পাশে ব্র্যাকেট `()` বসিয়ে কল করা হলে (temp(...)), ব্যাকগ্রাউন্ডে স্বয়ংক্রিয়ভাবে সেই অবজেক্টের __call__ method trigger হয়। অর্থাৎ এটি Internally 
run করে:
            complex_calculation = temp.__call__(complex_calculation)

PART 8: Wrapper Injection
Internal Mechanism: ContextDecorator এর ভেতরের __call__ মেথডটি অরিজিনাল ফাংশনটিকে একটি inner wrapper ফাংশন দিয়ে মুড়িয়ে দেয়:

def __call__(self, func):
    def inner(*args, **kwargs):
        with self: 
            return func(*args, **kwargs)
    return inner

PART 9: The Final Structure
Result: অরিজিনাল complex_calculation ফাংশনটি এখন সম্পূর্ণ রিপ্লেস হয়ে inner ফাংশনে রূপান্তরিত হয়ে গেছে। মেমোরিতে এর আসল স্ট্রাকচার এখন এইরকম:

def inner():
    with self: # self is the _GeneratorContextManager object
        time.sleep(0.5)
        print("Calculation inside the decorated function is complete.")
"""

"""
Phase 2: Runtime Execution Lifecycle

PART 10: complex_calculation() Call
যখন main program থেকে complex_calculation() call করা হয়, তখন মূলত ঐ নতুন inner() ফাংশনটি execute হওয়া শুরু করে।

PART 11: with self Block Trigger
inner এর ভেতরে থাকা `with self:` লাইনটি Encounter হওয়া মাত্রই python Internally _GeneratorContextManager.__enter__() method call করে।

PART 12: Generator Activation and The Yield Wait
পাইথনের ইন্টারনাল __enter__ মেথডটি বিল্ট-ইন next() ফাংশন দিয়ে জেনারেটরটিকে(execution_timer()) প্রথমবার active করে:

def __enter__(self):
    return next(self.gen)

next(self.gen) call হওয়ার কারণে জেনারেটরটি তার প্রথম লাইন থেকে execution হওয়া শুরু করে। এর ফলে start_time = time.monotonic() লাইনটি run হয়।
কোডটি চলতে চলতে যখনই try ব্লকের ভেতরের yield লাইনে পৌঁছায়, তখন জেনারেটরটি স্বভাবগতভাবেই pause হয়ে ওখানেই থমকে দাঁড়িয়ে থাকে। __enter__ মেথডটির কাজ 
এখানেই শেষ হয় এবং কন্ট্রোল আবার with ব্লকে ফিরে আসে

PART 13: Original Function Executes
জেনারেটরটি yield লাইনে pause থাকা অবস্থাতেই with ব্লকের ভেতরের main code run হয়:

time.sleep(0.5)
print("Calculation inside the decorated function is complete.")

PART 14: with Block Exit
Original ফাংশনের কাজ শেষ হওয়া মাত্রই with block থেকে বের হওয়ার সময় পাইথন Internally _GeneratorContextManager.__exit__() method call করে।

PART 15: Generator Resumption and Cleanup
পাইথনের interal __exit__ মেথডটি পুনরায় next() function call করে ঐ pause হয়ে থাকা জেনারেটরটিকে আবার active তোলে:

def __exit__(self, type, value, traceback):
    if type is None:
        next(self.gen)

জেনারেটরটি এবার yield লাইনের ঠিক পরের অংশ অর্থাৎ তার finally ব্লকে প্রবেশ করে এবং অবশিষ্ট কোডটুকু execute করে সম্পূর্ণ শেষ হয়ে যায় এবং একটি StopIteration 
exception raise করে।:
finally:
    end_time = time.monotonic()
    duration = end_time - start_time
    print(f"[{label}] Process took {duration:.4f} seconds.")
"""
