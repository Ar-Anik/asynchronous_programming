"""
iterables সম্পর্কে আলোচনা শুরু করা হবে একটি Sentence class implement করার মাধ্যমে: এর constructor-রে কিছু text সম্বলিত একটি
string প্রদান করা হলে, এটি work ধরে ধরে iterate করার সুবিধা দেয়। first step-এ sequence protocol implement করা হবে, এবং
এটি iterable কারণ সকল Sequence-ই iterable। এখন এর পেছনের actual কারণটি দেখা হবে।

Example-1 : একটি Sentence ক্লাস দেখানো হয়েছে যা index ব্যবহার করে text থেকে word গুলো আলাদা করে।
"""
import re
import reprlib

RE_WORD = re.compile(r'\w+')

class Sentence:
    def __init__(self, text):
        self.text = text
        self.words = RE_WORD.findall(text)

    def __getitem__(self, index):
        return self.words[index]

    def __len__(self):
        return len(self.words)

    def __repr__(self):
        return 'Sentence(%s)' % reprlib.repr(self.text)

"""
এখানে,
- .findall regular expression(re)-এর সাথে মিলে যাওয়া সকল nonoverlapping অংশগুলোকে string-এর একটি list হিসেবে return করে।
- self.words এর মধ্যে .findall এর ফলাফল save থাকে, তাই নির্দিষ্ট index অনুযায়ী word-টি return করা হয়।
- sequence protocol সম্পন্ন করার জন্য __len__ implement করা হয়েছে, যদিও একটি object-কে iterable করার জন্য এর কোনো প্রয়োজন নেই।
- reprlib.repr হলো একটি utility function যা অনেক বড় data structure-এর সংক্ষিপ্ত string representation তৈরি করতে ব্যবহৃত হয়।

Default ভাবে, reprlib.repr generate করা string-টিকে ৩০ character-এর মধ্যে সীমাবদ্ধ রাখে।
"""
# Test Result :
s = Sentence('"The time has come," the Walrus said,')
print(s)
"""
Sentence('"The time ha... Walrus said,')
"""

for word in s:
  print(word)

"""
The
time
has
come
the
Walrus
said
"""

print(list(s))
"""
['The', 'time', 'has', 'come', 'the', 'Walrus', 'said']
"""
