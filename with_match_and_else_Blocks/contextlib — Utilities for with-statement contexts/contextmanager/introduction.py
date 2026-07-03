# https://docs.python.org/3/library/contextlib.html

"""
@contextlib.contextmanager

পাইথনে with statement ব্যবহার করার জন্য সাধারণত একটি class তৈরি করতে হয় এবং তার ভেতরে enter ও exit method লিখতে হয়। তবে এই decorator ব্যবহার
করলে কোনো class তৈরি না করে, শুধুমাত্র একটি সাধারণ generator function লিখে with statement এর কাজ সম্পন্ন করা যায়।
যখন এমন কোনো resource (যেমন: file, database connection বা network socket) ব্যবহার করার প্রয়োজন হয় যা সরাসরি with statement সমর্থন করে না,
তখন সঠিক সময়ে তা active করা এবং কাজ শেষে তা release করা নিশ্চিত করতে এই decorator ব্যবহৃত হয়।
"""

# Smaple Code
from contextlib import contextmanager

@contextmanager
def managed_resource(*args, **kwargs):
    resource = acquire_resource(*args, **kwargs)

    try:
        yield resource
    finally:
        release_resource(resource)


with managed_resource(timeout=3600) as resource:
    pass


"""
-> How it work : 
- Provide Generator Iterator : এই decorator যুক্ত ফাংশনটি call করার পর এটি একটি generator-iterator তৈরি করে। এই ফাংশনের ভেতরে অবশ্যই ঠিক 
একটি yield থাকতে হবে। এই yield এর ডানপাশের মান বা অবজেক্টটি with ... as resource এর resource variable এর সাথে যুক্ত হয়।

- Execute Code : ফাংশনটি যখন yield লাইনে পৌঁছায়, তখন এর কার্যক্রম সাময়িকভাবে pause থাকে এবং with ব্লকের ভেতরের code run হওয়া শুরু করে।

- Again Run Code : with ব্লকের ভেতরের কাজ শেষ হওয়ার পর, pause থাকা ফাংশনটি ঠিক yield লাইনের পর থেকে আবার active হয় এবং finally ব্লকের code 
সম্পন্ন করে resource realease করে দেয়।
"""

"""
-> Error এবং Exception Management Rule
- যদি with ব্লকের কোড চলার সময় কোনো unhandled error বা exception ঘটে, তবে সেই error-টি জেনারেটর ফাংশনের ঠিক যেখানে yield হয়েছিল, সেখানে এসে 
disclose হয়।
- এই কারণে ফাংশনের ভেতরে try...except...finally ব্যবহার করা হয়। কোনো error ঘটলেও finally ব্লকটি অবশ্যই সম্পন্ন হয়, যা নিরাপদে resource release 
করতে সাহায্য করে।
- যদি error-টি শুধুমাত্র log করার জন্য বা অন্য কোনো কাজের জন্য except ব্লকে ধরা হয়, তবে ফাংশনের ভেতর থেকে সেই exception-টিকে অবশ্যই আবার raise 
করতে হবে।
- যদি exception পুনরায় raise করা না হয়, তবে এটি ধরে নেয় যে error-টি solve হয়ে গেছে। ফলে মূল প্রোগ্রামে কোনো error দেখাবে না এবং with স্টেটমেন্টের ঠিক 
পরের লাইন থেকে স্বাভাবিকভাবে কোড চলতে থাকবে।
"""

"""
পাইথন 3.2 version থেকে এটি ContextDecorator এর বৈশিষ্ট্য ধারণ করে। এর ফলে ফাংশনটি দিয়ে তৈরি Management-কে শুধু with statement-এই নয়, বরং অন্য 
কোনো ফাংশনের উপরে decorator হিসেবেও সরাসরি ব্যবহার করা যায়।

যখন ডেকোরেটর হিসেবে এটি ব্যবহৃত হয়, তখন প্রতিবার মূল ফাংশনটি call করার সময় অবিকল একটি নতুন generator instance তৈরি হয়। সাধারণত এই ধরনের object 
গুলো একবার ব্যবহারযোগ্য (one-shot) হলেও, এই নতুন instance তৈরির সুবিধার কারণে একই ফাংশন বারবার কল করা হলেও কোনো সমস্যা ছাড়াই এটি সফলভাবে কাজ 
করতে পারে।
"""

