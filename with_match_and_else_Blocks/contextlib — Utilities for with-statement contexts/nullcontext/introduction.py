"""
`nullcontext` বিষয়টি সহজভাবে বোঝার জন্য একটি বাস্তব জীবনের উদাহরণ দেওয়া যাক।

ধরুন, একটি ফাংশন বা কোড রয়েছে যা কোনো ডেটা ফাইলে লিখতে পারে, আবার সরাসরি কনসোলে (Screen) প্রিন্টও করতে পারে।

* যখন এটি **ফাইলে লেখে**, তখন ফাইলটি খোলার পর কাজ শেষে সেটি সঠিকভাবে বন্ধ করার জন্য একটি `context manager` (যেমন: `with open(...)`) প্রয়োজন হয়।
* কিন্তু যখন এটি **কনসোলে প্রিন্ট করে**, তখন কোনো ফাইল খোলার বা বন্ধ করার প্রয়োজন হয় না। অর্থাৎ, সেখানে কোনো `context manager`-এর দরকার নেই।

এখন, `nullcontext` ছাড়া এই ধরনের পরিস্থিতিতে কোড লিখতে গেলে একই কাজের জন্য আলাদা আলাদা `if-else` ব্লক তৈরি করতে হয়, যা কোডকে জটিল করে তোলে। `nullcontext` এখানে একটি ছদ্ম বা নকল (dummy/stand-in) `context manager` হিসেবে কাজ করে, যা কোনো কাজ না করেই `with` ব্লকের গঠনটিকে ঠিক রাখে।

নিচে একটি গভীর ও বিস্তারিত বর্ণনাসহ উদাহরণ দেওয়া হলো:

---

### **nullcontext ছাড়া কোড (জটিল পদ্ধতি)**

যদি `nullcontext` ব্যবহার করা না হয়, তবে ফাইলের ক্ষেত্রে এবং কনসোলের ক্ষেত্রে আলাদাভাবে `logic check` করতে হয়:

```python
import sys

def save_data(filename=None):
    text_to_save = "Python Contextlib Utilities"

    if filename:
        # ফাইলের জন্য context manager ব্যবহার করা হচ্ছে
        with open(filename, 'w') as file:
            file.write(text_to_save)
    else:
        # কনসোলের জন্য আলাদা logic, কারণ এখানে কোনো context manager নেই
        sys.stdout.write(text_to_save)

```

এখানে লক্ষ্য করলে দেখা যাবে, ডেটা লেখার মূল কাজটি (`write`) দুই জায়গায় আলাদাভাবে লিখতে হয়েছে, যা কোডের পুনরাবৃত্তি ঘটায়।

---

### **nullcontext ব্যবহার করে কোড (সহজ ও সুন্দর পদ্ধতি)**

`nullcontext` ব্যবহার করলে পুরো `conditional logic`-টি `with` ব্লকের বাইরে চলে আসে এবং মূল লেখার কাজটি মাত্র একবারই লিখতে হয়:

```python
import contextlib
import sys

def save_data(filename=None):
    text_to_save = "Python Contextlib Utilities"

    # conditional code যা ঠিক করবে কোন context manager ব্যবহার করা হবে
    if filename:
        context_manager = open(filename, 'w')
    else:
        # ফাইল না থাকলে nullcontext একটি বিকল্প (stand-in) হিসেবে কাজ করবে
        # এটি sys.stdout-কে সরাসরি রিটার্ন করবে এবং কোনো close() মেথড রান করবে না
        context_manager = contextlib.nullcontext(sys.stdout)

    # এখন মাত্র একটি একক with ব্লক দিয়েই সম্পূর্ণ কাজ সম্পন্ন করা সম্ভব
    with context_manager as destination:
        destination.write(text_to_save)

```

### **এখানে ঠিক কী ঘটছে?**

1. **ফাইল থাকলে (`filename` দেওয়া হলে):** `context_manager` হিসেবে `open(filename, 'w')` সেট হয়। `with` ব্লকটি ফাইলের `__enter__` মেথড কল করে ফাইলটি খোলে এবং কাজ শেষে `__exit__` মেথড কল করে ফাইলটি স্বয়ংক্রিয়ভাবে বন্ধ (automatic close) করে।
2. **ফাইল না থাকলে (`filename` না দেওয়া হলে):** `context_manager` হিসেবে `nullcontext(sys.stdout)` সেট হয়। `with` ব্লকটি যখন শুরু হয়, তখন `nullcontext` কোনো রকম ফাইল ওপেন করার ঝামেলা ছাড়াই সরাসরি `sys.stdout`-কে `destination` variable-এর কাছে পাঠিয়ে দেয়। আর যখন `with` ব্লকটি শেষ হয়, তখন এটি কোনো `close` মেথড বা অন্য কোনো অ্যাকশন (command) এক্সিকিউট (execute) করে না।

> **সংক্ষেপে:** `nullcontext` হলো একটি "ফাঁকা বা নিষ্ক্রিয়" `context manager`। যখন কোডের কোনো এক জায়গায় `context manager` এর প্রয়োজন হয় এবং অন্য জায়গায় প্রয়োজন হয় না, তখন দুই জায়গার কোডের গঠন বা স্ট্রাকচার (syntax) একই রকম রাখার জন্য এটি ব্যবহার করা হয়।
"""