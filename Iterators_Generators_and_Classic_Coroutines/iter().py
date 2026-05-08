"""
Q : Why Sequences Are Iterable?
পাইথনে যখনই কোনো object x-কে iterate করার প্রয়োজন হয়, তখন python automatically iter(x) কল করে। এই iter function-টি নিচের ধাপগুলো অনুসরণ করে:
১. এটি প্রথমে check করে object-টি __iter__ implement করে কি না, এবং করলে সেটি call করে একটি iterator collect করে।
২. যদি __iter__ না থাকে, কিন্তু __getitem__ থাকে, তবে iter() একটি iterator তৈরি করে যা 0(zero) index থেকে item গুলো fetch করার চেষ্টা করে।
৩. যদি এই দুটিই ব্যর্থ হয়, তবে পাইথন TypeError দেয় (সাধারণত: 'C' object is not iterable)।

এ কারণেই সব Python sequence-ই iterable, কারণ তারা __getitem__ implement করে। যদিও standard sequence-গুলো __iter__ ও implement করে, এবং আমাদেরও সেটি করা উচিত; কারণ __getitem__-এর মাধ্যমে iteration পদ্ধতিটি মূলত backward compatibility-র জন্য রাখা হয়েছে।
এটি duck typing-এর একটি বড় উদাহরণ, একটি object-কে শুধু তখনই iterable ধরা হয় না যখন তার __iter__ আছে, বরং __getitem__ থাকলেও তাকে iterable হিসেবে গণ্য করা হয়।

Goose-typing approach:
এখানে ইটারেবলের সংজ্ঞা আরও নির্দিষ্ট, একটি object-কে তখনই iterable বলা হবে যদি এটি __iter__ method-টি implement করে।
from collections import abc
isinstance(goose_spam_can, abc.Iterable)


Duck Typing ও Goose Typing-এর পার্থক্য:
1. Duck Typing: কোনো ক্লাসে শুধু __getitem__ থাকলেও python তাকে iterable হিসেবে ব্যবহার করতে পারে। কিন্তু isinstance(obj, abc.Iterable) check করলে সেটি False আসবে।
2. Goose Typing: যদি ক্লাসে __iter__ method থাকে, তবে সেটি isinstance(obj, abc.Iterable) check করলে সেটি True আসবে।

class GooseSpam:
    def __iter__(self):
        pass

from collections.abc import Iterable
print(isinstance(GooseSpam, Iterable))

goose_spam_can = GooseSpam()
print(isinstance(goose_spam_can, Iterable))

Note : কোনো অবজেক্ট iterable কি না তা check করার সবচেয়ে সঠিক উপায় হলো iter(x) call করে দেখা। যদি এটি iterable না হয়, তবে পাইথন TypeError দিবে। এটি isinstance চেক করার চেয়ে বেশি নির্ভুল।


Using iter with a Callable
আমরা iter()-কে দুটি argument দিয়ে call করে কোনো function বা callable object থেকে iterator তৈরি করতে পারি।
1. First argument: একটি callable object (যাকে বারবার call করা হবে)।
2. Second argument: একটি sentinel (এটি একটি marker value; যখন callable-টি এই value-টি return করবে, তখন iteration বন্ধ হয়ে যাবে)।

Example: একটি ছক্কা/die 6 পর্যন্ত roll করা, কিন্তু 1 উঠলে থেমে যাওয়া:
from random import randint

def d6():
    return randint(1, 6)

d6_iter = iter(d6, 1)
print(d6_iter)

for roll in d6_iter:
    print(roll)

এখানে loop টি কখনোই 1 print করবে না, কারণ 1 হলো sentinel value যা stop single হিসেবে কাজ করে।

iter() এর এই second example টি হলো block-reader তৈরি করা। উদাহরণস্বরূপ ফাইলের শেষ প্রান্তে না পৌঁছানো পর্যন্ত একটি binary file থেকে নির্দিষ্ট-প্রস্থের block read করা:
from functools import partial
with open('mydata.db', 'rb') as f:
    read64 = partial(f.read, 64)
    print(read64.__dir__())
    for block in iter(read64, b''):
        print(f"Processing block of size: {len(block)} bytes")
        print(f"Content (hex): {block}...")


from, print(read64.__dir__()) we found :
['__repr__', '__call__', '__getattribute__', '__setattr__', '__delattr__', '__new__', '__reduce__', '__setstate__', 'func', 'args', 'keywords', '__dict__', '__doc__', '__hash__', '__str__', '__lt__', '__le__', '__eq__', '__ne__', '__gt__', '__ge__', '__init__', '__reduce_ex__', '__subclasshook__', '__init_subclass__', '__format__', '__sizeof__', '__dir__', '__class__']

Q : read64.__dir__() লিস্টে __iter__ বা __getitem__ না থাকা সত্ত্বেও এটি কীভাবে কাজ করছে?

"""