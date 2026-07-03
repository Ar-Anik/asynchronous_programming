"""
এখানে আপনার দেওয়া পাইথন স্ক্রিপ্ট এবং টেক্সটের সম্পূর্ণ ও বিস্তারিত বাংলা অনুবাদ প্রদান করা হলো। আপনার পূর্বের নির্দেশনা অনুযায়ী কোনো ধরনের নির্দিষ্ট সম্বোধনবাচক শব্দ পরিহার করা হয়েছে এবং উল্লেখিত নির্দিষ্ট শব্দগুলোর ক্ষেত্রে যথাযথ ইংরেজি বা বিশুদ্ধ বাংলা শব্দ ব্যবহার করা হয়েছে।

### **১. `charindex.py` কোড**
"""
import sys
import unicodedata
from collections import defaultdict
from collections.abc import Iterator

STOP_CODE: int = sys.maxunicode + 1

Char = str
Index = defaultdict[str, set[Char]]

def tokenize(text: str) -> Iterator[str]:
    """return iterator of uppercased words"""
    for word in text.upper().replace('-', ' ').split():
        yield word

class InvertedIndex:
    entries: Index

    def __init__(self, start: int = 32, stop: int = STOP_CODE):
        entries: Index = defaultdict(set)
        for char in (chr(i) for i in range(start, stop)):
            name = unicodedata.name(char, '')
            if name:
                for word in tokenize(name):
                    entries[word].add(char)
        self.entries = entries

    def search(self, query: str) -> set[Char]:
        if words := list(tokenize(query)):
            found = self.entries[words[0]]
            return found.intersection(*(self.entries[w] for w in words[1:]))
        else:
            return set()

def format_results(chars: set[Char]) -> Iterator[str]:
    for char in sorted(chars):
        name = unicodedata.name(char)
        code = ord(char)
        yield f'U+{code:04X}\t{char}\t{name}'

def main(words: list[str]) -> None:
    if not words:
        print('Please give one or more words to search.')
        sys.exit(2)  # command line usage error
    index = InvertedIndex()
    # print("Nothing : ", index.entries)
    chars = index.search(' '.join(words))
    for line in format_results(chars):
        print(line)
    print('─' * 66, f'{len(chars)} found')

if __name__ == '__main__':
    main(sys.argv[1:])

"""
২. একটি FastAPI Web Service**

পরবর্তী উদাহরণটি, অর্থাৎ `web_mojifinder.py`, FastAPI ব্যবহার করে তৈরি করা হয়েছে। এটি একটি Python ASGI Web framework, যা ৭৩২ পৃষ্ঠায় "ASGI—Asynchronous Server Gateway Interface" অংশে আলোচনা করা হয়েছে।

২১-২ চিত্রে (Figure 21-2) ফ্রন্টএন্ডের একটি স্ক্রিনশট দেখা যায়। এটি একটি অত্যন্ত সাধারণ SPA (Single Page Application): প্রথমবার HTML ডাউনলোড হওয়ার পর ক্লায়েন্ট-সাইড JavaScript সার্ভারের সাথে যোগাযোগ করে UI আপডেট করে।

FastAPI মূলত SPA এবং মোবাইল অ্যাপ্লিকেশনের জন্য ব্যাকএন্ড তৈরি করার উদ্দেশ্যে তৈরি করা হয়েছে, যা সাধারণত সার্ভার-রেন্ডার করা HTML-এর পরিবর্তে JSON রেসপন্স প্রদানকারী web API এন্ডপয়েন্টগুলোর সমন্বয়ে কাজ করে।

ওয়েব API-এর জন্য প্রয়োজনীয় অতিরিক্ত কোড (boilerplate code) দূর করতে FastAPI ডেকোরেটর, টাইপ হিন্টস এবং কোড ইন্ট্রোস্পেকশন ব্যবহার করে থাকে। একই সাথে এটি তৈরি করা API-গুলোর জন্য স্বয়ংক্রিয়ভাবে ইন্টারেক্টিভ OpenAPI (যা Swagger নামেও পরিচিত) ডকুমেন্টেশন প্রকাশ করে। প্রদত্ত চিত্রে (Figure 21-4) `web_mojifinder.py`-এর জন্য স্বয়ংক্রিয়ভাবে তৈরি হওয়া `/docs` পেজটি দেখা যাচ্ছে, যেখানে `/search` এন্ডপয়েন্টটির স্কিমা বিস্তারিতভাবে দেওয়া রয়েছে।

**উদাহরণ ২১-১১**-এ `web_mojifinder.py`-এর কোড দেওয়া হয়েছে, তবে এটি শুধুমাত্র ব্যাকএন্ড কোড। রুট URL `/`-এ রিকোয়েস্ট পাঠানো হলে সার্ভার `form.html` ফাইলটি পাঠায়, যেখানে ৮১ লাইনের কোড রয়েছে। এর মধ্যে ৫৪ লাইন JavaScript কোড সার্ভারের সাথে যোগাযোগ করতে এবং ফলাফল দিয়ে একটি টেবিল পূরণ করতে ব্যবহৃত হয়। ফ্রেমওয়ার্ক-বিহীন সাধারণ JavaScript কোড পড়ার আগ্রহ থাকলে Fluent Python-এর কোড রিপোজিটরিতে `21-async/mojifinder/static/form.html` ফাইলটি দেখা যেতে পারে।

`web_mojifinder.py` রান করার জন্য দুটি প্যাকেজ এবং তাদের ডিপেন্ডেন্সি ইন্সটল করা প্রয়োজন: FastAPI এবং uvicorn। ডেভেলপমেন্ট মোডে uvicorn-এর সাহায্যে উদাহরণ ২১-১১ রান করার command-টি হলো:

```bash
$ uvicorn web_mojifinder:app --reload

```

এখানে ব্যবহৃত প্যারামিটারগুলো হলো:

* **`web_mojifinder:app`**: প্যাকেজের নাম, একটি কোলন এবং এর মধ্যে সংজ্ঞায়িত করা ASGI অ্যাপ্লিকেশনের নাম—সাধারণত এই নাম `app` রাখা হয়।
* **`--reload`**: এর মাধ্যমে অ্যাপ্লিকেশনের সোর্স ফাইলগুলোতে হওয়া পরিবর্তনগুলো uvicorn পর্যবেক্ষণ করে এবং স্বয়ংক্রিয়ভাবে সেগুলোকে রিলোড করে। এটি শুধুমাত্র ডেভেলপমেন্টের সময় কার্যকর।

এখন `web_mojifinder.py`-এর সোর্স কোডটি বিস্তারিতভাবে দেখা যাক।

---

### **৩. `web_mojifinder.py` কোড**

"""
# Example 21-11. web_mojifinder.py: complete source
from pathlib import Path
from unicodedata import name
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from charindex import InvertedIndex

STATIC_PATH = Path(__file__).parent.absolute() / 'static'

app = FastAPI(
    title='Mojifinder Web',
    description='Search for Unicode characters by name.',
)

class CharName(BaseModel):
    char: str
    name: str

def init(app):
    app.state.index = InvertedIndex()
    app.state.form = (STATIC_PATH / 'form.html').read_text()

init(app)

@app.get('/search', response_model=list[CharName])
async def search(q: str):
    chars = sorted(app.state.index.search(q))
    return ({'char': c, 'name': name(c)} for c in chars)

@app.get('/', response_class=HTMLResponse, include_in_schema=False)
def form():
    return app.state.form

# no main funcion

"""
৪. কোডের বিস্তারিত ব্যাখ্যা**

1. এই অধ্যায়ের মূল প্রসঙ্গের সাথে সরাসরি যুক্ত না হলেও এটি লক্ষ্য করার মতো একটি বিষয়: `pathlib` দ্বারা ওভারলোড করা `/` অপারেটরের চমৎকার ব্যবহার।
2. এই লাইনে ASGI অ্যাপটিকে সংজ্ঞায়িত করা হয়েছে। এটি `app = FastAPI()` এর মতো সাধারণও হতে পারে। এখানে দেখানো প্যারামিটারগুলো স্বয়ংক্রিয়ভাবে তৈরি হওয়া ডকুমেন্টেশনের মেটাডেটা।
3. JSON রেসপন্সের জন্য একটি pydantic স্কিমা, যেখানে `char` এবং `name` ফিল্ডগুলো রয়েছে।
4. ইনডেক্সটি তৈরি করা হয়েছে এবং স্ট্যাটিক HTML ফর্মটি লোড করা হয়েছে, পরবর্তীতে ব্যবহারের জন্য উভয়কেই `app.state`-এর সাথে যুক্ত করা হয়েছে।
5. ASGI সার্ভার দ্বারা এই মডিউলটি লোড হওয়ার সময় `init` ফাংশনটি রান করানো হয়।
6. `/search` এন্ডপয়েন্টের জন্য রাউট; রেসপন্সের ফরম্যাট বর্ণনা করতে `response_model` হিসেবে `CharName` pydantic মডেলটি ব্যবহার করা হয়েছে।
7. FastAPI ধরে নেয় যে, ফাংশন বা কোরুটিন সিগনেচারে উপস্থিত থাকা কোনো প্যারামিটার যদি রাউটের পাথে না থাকে, তবে তা HTTP কোয়েরি স্ট্রিংয়ে পাঠানো হবে (যেমন: `/search?q=cat`)। যেহেতু `q`-এর কোনো ডিফল্ট মান নেই, কোয়েরি স্ট্রিং থেকে `q` অনুপস্থিত থাকলে FastAPI একটি ৪২২ (Unprocessable Entity) স্ট্যাটাস রিটার্ন করবে। 
8.`response_model` স্কিমার সাথে সামঞ্জস্যপূর্ণ ডিকশনারির একটি ইটারেবল রিটার্ন করার ফলে FastAPI `@app.get` ডেকোরেটরে থাকা `response_model` অনুযায়ী JSON রেসপন্স তৈরি করতে পারে।
9. রেসপন্স তৈরি করতে সাধারণ ফাংশনও (অর্থাৎ, non-async ফাংশন) ব্যবহার করা যেতে পারে।
10. এই মডিউলে কোনো `main` ফাংশন নেই। এটি ASGI সার্ভার দ্বারা লোড ও পরিচালিত হয়—এই উদাহরণের ক্ষেত্রে যা হলো uvicorn।


উদাহরণ ২১-১১-এ `asyncio`-কে সরাসরি কল করা হয়নি। FastAPI মূলত Starlette ASGI টুলকিটের ওপর ভিত্তি করে তৈরি, যা মূলত `asyncio` ব্যবহার করে থাকে।

আরও লক্ষ্য করা যায় যে, `search` ফাংশনটির ভেতরে `await`, `async with`, বা `async for` ব্যবহার করা হয়নি, তাই এটি একটি সাধারণ ফাংশনও হতে পারত। `search`-কে একটি কোরুটিন হিসেবে সংজ্ঞায়িত করা হয়েছে শুধুমাত্র এটি বোঝানোর জন্য যে, FastAPI জানে কীভাবে এটিকে পরিচালনা করতে হয়। একটি বাস্তব অ্যাপ্লিকেশনে বেশিরভাগ এন্ডপয়েন্ট ডাটাবেস থেকে কোয়েরি করে অথবা অন্যান্য রিমোট সার্ভারে রিকোয়েস্ট পাঠায়। তাই FastAPI (এবং সামগ্রিকভাবে ASGI ফ্রেমওয়ার্কগুলোর) একটি অন্যতম গুরুত্বপূর্ণ সুবিধা হলো কোরুটিনগুলোর প্রতি এর সমর্থন, যা নেটওয়ার্ক I/O-এর জন্য অ্যাসিঙ্ক্রোনাস লাইব্রেরিগুলোর সুবিধা নিতে পারে।

স্ট্যাটিক HTML ফর্ম লোড ও সার্ভ করার জন্য `init` এবং `form` ফাংশনগুলো লেখা হয়েছে, যা মূলত উদাহরণটিকে ছোট এবং সহজে রান করার উপযোগী একটি পদ্ধতি। প্রস্তাবিত সর্বোত্তম পদ্ধতি হলো, সমস্ত স্ট্যাটিক অ্যাসেট পরিচালনা করার জন্য ASGI সার্ভারের সামনে একটি প্রক্সি বা লোড-ব্যালান্সার রাখা এবং সম্ভব হলে একটি CDN ব্যবহার করা। এরকম একটি প্রক্সি/লোড-ব্যালান্সার হলো Traefik, যা নিজেকে একটি "edge router" হিসেবে বর্ণনা করে। এটি `system`-এর পক্ষ থেকে রিকোয়েস্টগুলো গ্রহণ করে এবং কোন কম্পোনেন্টগুলো সেগুলো পরিচালনার জন্য দায়ী তা খুঁজে বের করে। কোডকে সেভাবে প্রস্তুত করার জন্য FastAPI-তে প্রজেক্ট জেনারেশন স্ক্রিপ্ট রয়েছে।

টাইপিং সম্পর্কে আগ্রহীরা হয়তো লক্ষ্য করে থাকবেন যে, `search` এবং `form` ফাংশনে কোনো রিটার্ন টাইপ হিন্ট নেই। এর পরিবর্তে, FastAPI রাউট ডেকোরেটরগুলোতে `response_model=` কিওয়ার্ড আর্গুমেন্টের ওপর নির্ভর করে।

FastAPI ডকুমেন্টেশনের "Response Model" পেজে এ সম্পর্কে বিস্তারিতভাবে বর্ণনা করা হয়েছে:

> "রেসপন্স মডেলটিকে ফাংশনের রিটার্ন টাইপ অ্যানোটেশন হিসেবে লেখার পরিবর্তে এই প্যারামিটারে ঘোষণা করা হয়, কারণ পাথ ফাংশনটি হয়তো সরাসরি সেই রেসপন্স মডেলটি রিটার্ন করে না, বরং এটি একটি dict, ডাটাবেস `object` বা অন্য কোনো মডেল রিটার্ন করতে পারে। এরপর `response_model` ব্যবহার করে ফিল্ড লিমিটিং এবং সিরিয়ালাইজেশন সম্পন্ন করা হয়।"

উদাহরণস্বরূপ, `search` ফাংশনে `CharName` `object`-এর কোনো তালিকার পরিবর্তে dict আইটেমের একটি জেনারেটর রিটার্ন করা হয়েছে। কিন্তু ডেটা `validate` করতে এবং `response_model=list[CharName]`-এর সাথে সামঞ্জস্য রেখে উপযুক্ত JSON রেসপন্স তৈরি করতে FastAPI এবং pydantic-এর জন্য এটিই যথেষ্ট।

"""
