"""
## একটি asyncio TCP Server

`tcp_mojifinder.py` প্রোগ্রামটি একটি ক্লায়েন্ট (যেমন Telnet বা Netcat) এর সাথে যোগাযোগের জন্য প্লেইন TCP ব্যবহার করে। তাই এটি কোনো এক্সটার্নাল ডিপেন্ডেন্সি (external dependency) ছাড়াই এবং HTTP রিইনভেন্ট (reinvent) না করেই `asyncio` ব্যবহার করে তৈরি করা সম্ভব। চিত্র "figure-21.5.jpg"-এ একটি `text`-ভিত্তিক ইউজার ইন্টারফেস (UI) দেখানো হয়েছে।

---

### figure-21.5.jpg চিত্রের বর্ণনা

এই চিত্রে একটি Telnet সেশন দেখানো হয়েছে যেখানে ক্লায়েন্ট `tcp_mojifinder.py` সার্ভারের সাথে যুক্ত হয়ে "fire" শব্দের জন্য কুয়েরি (query) পাঠিয়েছে। টার্মিনালে `telnet localhost 2323` `command` চালানোর পর এটি লোকালহোস্টের `127.0.0.1` আইপি (IP) এবং `2323` পোর্টে সংযুক্ত হয়। এরপর সার্ভার থেকে একটি প্রম্পট `?>` প্রদর্শিত হয়। সেখানে "fire" শব্দটি ইনপুট দেওয়ার পর, সার্ভার ইউনিকোড ক্যারেক্টার ইনডেক্স থেকে "fire" শব্দটির সাথে সম্পর্কিত ১১টি ফলাফল খুঁজে বের করে প্রদর্শন করে। প্রতিটি ফলাফলে ইউনিকোড কোডপয়েন্ট (যেমন: U+1F525), ক্যারেক্টার সিম্বল (যেমন: 🔥) এবং ক্যারেক্টারের নাম (যেমন: FIRE) ক্রমানুসারে সাজানো রয়েছে। সর্বশেষে একটি রেখা টেনে "11 found" লিখে মোট ফলাফলের সংখ্যা দেখানো হয়েছে।

---

এই প্রোগ্রামটি `web_mojifinder.py` এর চেয়ে আকারে দ্বিগুণ বড়, তাই এর প্রেজেন্টেশনকে তিনটি অংশে ভাগ করা হয়েছে: Example 21-12, Example 21-14 এবং Example 21-15। `tcp_mojifinder.py` এর উপরের অংশ—যার মধ্যে ইমপোর্ট স্টেটমেন্টগুলো রয়েছে—তা Example 21-14 এ দেওয়া হয়েছে, তবে প্রথমে `supervisor` coroutine এবং প্রোগ্রামের মূল চালিকাশক্তি `main` ফাংশনটি বর্ণনা করা হলো।

### Example 21-12. tcp_mojifinder.py: একটি সাধারণ TCP সার্ভার; Example 21-14 এ চলমান

```python
async def supervisor(index: InvertedIndex, host: str, port: int) -> None:
    server = await asyncio.start_server(functools.partial(finder, index), host, port)
    socket_list = cast(tuple[TransportSocket, ...], server.sockets)
    addr = socket_list[0].getsockname()
    print(f'Serving on {addr}. Hit CTRL-C to stop.')
    await server.serve_forever()


def main(host: str = '127.0.0.1', port_arg: str = '2323'):
    port = int(port_arg)
    print('Building index.')
    index = InvertedIndex()
    try:
        asyncio.run(supervisor(index, host, port))
    except KeyboardInterrupt:
        print('\nServer shut down.')


if __name__ == '__main__':
    main(*sys.argv[1:])

```

1. এই `await` দ্রুত `asyncio.Server` এর একটি ইনস্ট্যান্স তৈরি করে, যা একটি TCP সকেট সার্ভার। ডিফল্টভাবে, `start_server` সার্ভার তৈরি এবং চালু করে, যা কানেকশন গ্রহণ করার জন্য প্রস্তুত থাকে।
2. `start_server`-এর প্রথম আর্গুমেন্ট হলো `client_connected_cb`, যা একটি নতুন ক্লায়েন্ট কানেকশন শুরু হলে রান করার জন্য একটি `callback` হিসেবে কাজ করে। এই `callback` একটি সাধারণ ফাংশন বা একটি coroutine হতে পারে, তবে এটিকে অবশ্যই ঠিক দুটি আর্গুমেন্ট গ্রহণ করতে হবে: একটি `asyncio.StreamReader` এবং একটি `asyncio.StreamWriter`। তবে, এই প্রোগ্রামের `finder` coroutine-এর একটি ইনডেক্স (index) প্রয়োজন, তাই `functools.partial` ব্যবহার করে সেই প্যারামিটারটি বাইন্ড (bind) করা হয়েছে এবং এমন একটি ক্যালেবল (callable) অবজেক্ট পাওয়া গেছে যা রিডার এবং রাইটার গ্রহণ করে। ইউজার ফাংশনগুলোকে `callback` API-এর সাথে মানিয়ে নেওয়ার জন্য `functools.partial` এর ব্যবহার সবচেয়ে সাধারণ একটি উদাহরণ।
3. `host` এবং `port` হলো `start_server`-এর দ্বিতীয় ও তৃতীয় আর্গুমেন্ট। এর পূর্ণাঙ্গ সিগনেচার `asyncio` ডকুমেন্টেশনে দেখা যাবে।
4. এই `cast` প্রয়োজন হয়েছে কারণ মে ২০২১ পর্যন্ত `Server` ক্লাসের sockets প্রোপার্টির জন্য typeshed-এ একটি পুরানো টাইপ হিন্ট (type hint) ছিল। বিস্তারিত তথ্য typeshed-এর Issue #5535-এ রয়েছে।
5. সার্ভারের প্রথম সকেটের অ্যাড্রেস এবং পোর্ট প্রদর্শন করা হয়।
6. যদিও `start_server` ইতিমধ্যেই একটি কনকারেন্ট টাস্ক (concurrent task) হিসেবে সার্ভার চালু করেছে, তবুও `server.serve_forever()` মেথডটিতে `await` করা প্রয়োজন যাতে `supervisor` এখানে সাসপেন্ড (suspended) অবস্থায় থাকে। এই লাইনটি না থাকলে, `supervisor` অবিলম্বে রিটার্ন করত, যার ফলে `asyncio.run(supervisor(…))` দ্বারা শুরু হওয়া লুপটি শেষ হয়ে যেত এবং প্রোগ্রাম থেকে প্রস্থান (exit) করত। `Server.serve_forever` এর ডকুমেন্টেশন অনুযায়ী: "যদি সার্ভার ইতিমধ্যেই কানেকশন গ্রহণ করতে প্রস্তুত থাকে, তবে এই মেথডটি কল করা যেতে পারে।"
7. ইনভার্টেড ইনডেক্স (Inverted Index) তৈরি করা হয়।
8. `supervisor` রান করানোর জন্য ইভেন্ট লুপ (`event loop`) শুরু করা হয়।
9. টার্মিনালে Ctrl-C চেপে সার্ভার বন্ধ করার সময় যেন কোনো বিরক্তিকর ট্রেসব্যাক (traceback) দেখা না যায়, সেজন্য `KeyboardInterrupt` ক্যাচ (catch) করা হয়েছে।

---

`tcp_mojifinder.py`-তে কন্ট্রোল ফ্লো (control flow) কীভাবে কাজ করে তা সহজে বোঝার জন্য, সার্ভার কনসোলে উৎপন্ন হওয়া আউটপুট লক্ষ্য করা যেতে পারে, যা Example 21-13-এ তালিকাভুক্ত করা হয়েছে।

### Example 21-13. tcp_mojifinder.py: এটি চিত্র 21-5 এ চিত্রিত সেশনের সার্ভার সাইড

```
$ python3 tcp_mojifinder.py
Building index.
Serving on ('127.0.0.1', 2323). Hit Ctrl-C to stop.
 From ('127.0.0.1', 58192): 'cat face'
 To ('127.0.0.1', 58192): 10 results.
 From ('127.0.0.1', 58192): 'fire'
 To ('127.0.0.1', 58192): 11 results.
 From ('127.0.0.1', 58192): '\x00'
Close ('127.0.0.1', 58192).
^C
Server shut down.
$

```

1. `main` ফাংশন দ্বারা উৎপন্ন আউটপুট। পরবর্তী লাইনটি দৃশ্যমান হওয়ার আগে, ইনডেক্স তৈরি হওয়ার জন্য মেশিনে প্রায় ০.৬ সেকেন্ডের বিলম্ব (delay) ঘটে।
2. `supervisor` দ্বারা উৎপন্ন আউটপুট।
3. `finder`-এর একটি `while` লুপের প্রথম ইটারেশন (iteration)। TCP/IP স্ট্যাক Telnet ক্লায়েন্টকে ৫৮১৯২ পোর্ট বরাদ্দ করেছে। যদি সার্ভারে একাধিক ক্লায়েন্ট কানেক্ট করা হয়, তবে আউটপুটে তাদের বিভিন্ন পোর্ট নম্বর দেখা যাবে।
4. `finder`-এর `while` লুপের দ্বিতীয় ইটারেশন।
5. ক্লায়েন্ট টার্মিনালে Ctrl-C চাপলে `finder`-এর `while` লুপটি বন্ধ (exit) হয়ে যায়।
6. `finder` coroutine এই মেসেজটি প্রদর্শন করে এবং শেষ হয়ে যায়। ইতিমধ্যে সার্ভারটি সচল থাকে এবং অন্য কোনো ক্লায়েন্টকে সার্ভিস দেওয়ার জন্য প্রস্তুত থাকে।
7. সার্ভার টার্মিনালে Ctrl-C চাপলে `server.serve_forever` বাতিল (cancelled) হয়ে যায়, যা `supervisor` এবং ইভেন্ট লুপের সমাপ্তি ঘটায়।
8. `main` ফাংশন দ্বারা উৎপন্ন আউটপুট।

---

`main` ফাংশন ইনডেক্স তৈরি করার পর এবং ইভেন্ট লুপ শুরু করার পর, `supervisor` দ্রুত `Serving on…` মেসেজটি প্রদর্শন করে এবং `await server.serve_forever()` লাইনে সাসপেন্ড হয়ে যায়। সেই মুহূর্তে, কন্ট্রোল ফ্লো ইভেন্ট লুপের মধ্যে চলে যায় এবং সেখানেই অবস্থান করে। মাঝে মাঝে এটি `finder` coroutine-এ ফিরে আসে, যা নেটওয়ার্কের মাধ্যমে ডেটা পাঠানো বা গ্রহণের জন্য অপেক্ষা করার প্রয়োজন হলেই কন্ট্রোল আবার ইভেন্ট লুপের কাছে ফিরিয়ে দেয়।

ইভেন্ট লুপ সচল থাকা অবস্থায়, সার্ভারের সাথে সংযুক্ত প্রতিটি ক্লায়েন্টের জন্য `finder` coroutine-এর একটি নতুন ইনস্ট্যান্স শুরু হবে। এইভাবে, এই সাধারণ সার্ভারটি দ্বারা একসঙ্গে অনেক ক্লায়েন্ট কনকারেন্টলি (concurrently) হ্যান্ডেল করা সম্ভব। সার্ভারে একটি `KeyboardInterrupt` না ঘটা পর্যন্ত বা ওএস (OS) দ্বারা এর প্রসেসটি কিল (kill) না হওয়া পর্যন্ত এই প্রক্রিয়া চলতে থাকে।

এখন `tcp_mojifinder.py` এর উপরের অংশ এবং `finder` coroutine-টি দেখা যাক।

---

### Example 21-14. tcp_mojifinder.py: Example 21-12 এর পর থেকে চলমান

```python
import asyncio
import functools
import sys
from asyncio.trsock import TransportSocket
from typing import cast

from charindex import InvertedIndex, format_results

CRLF = b'\r\n'
PROMPT = b'?> '

async def finder(index: InvertedIndex, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    client = writer.get_extra_info('peername')
    while True:
        writer.write(PROMPT)  # can't await!
        await writer.drain()  # must await!
        data = await reader.readline()
        if not data:
            break
        try:
            query = data.decode().strip()
        except UnicodeDecodeError:
            query = '\x00'
        print(f' From {client}: {query!r}')
        if query:
            if ord(query[:1]) < 32:
                break

            results = await search(query, index, writer)
            print(f' To {client}: {results} results.')

    writer.close()
    await writer.wait_closed()
    print(f'Close {client}.')

```

1. `format_results` ফাংশনটি একটি `text`-ভিত্তিক ইউজার ইন্টারফেসে (যেমন: কমান্ড লাইন বা টেলনেট সেশন) `InvertedIndex.search`-এর ফলাফল প্রদর্শনের জন্য দরকারী।
2. `finder`-কে `asyncio.start_server`-এ পাস করার জন্য এটিকে `functools.partial` দিয়ে র‍্যাপ (wrap) করা হয়েছে, কারণ সার্ভার এমন একটি coroutine বা ফাংশন প্রত্যাশা করে যা কেবল রিডার এবং রাইটার আর্গুমেন্ট গ্রহণ করে।
3. সকেটটি যে রিমোট ক্লায়েন্ট অ্যাড্রেসের সাথে সংযুক্ত, তা সংগ্রহ করা হয়।
4. ক্লায়েন্ট থেকে একটি কন্ট্রোল ক্যারেক্টার (control character) না পাওয়া পর্যন্ত এই লুপটি একটি ডায়ালগ হ্যান্ডেল করে।
5. `StreamWriter.write` মেথডটি কোনো coroutine নয়, এটি একটি সাধারণ ফাংশন; এই লাইনটি `?>` প্রম্পটটি পাঠায়।
6. `StreamWriter.drain` রাইটার বাফারটি ফ্লাশ (flush) করে; এটি একটি coroutine, তাই এটিকে অবশ্যই `await` দিয়ে চালিত করতে হবে।
7. `StreamWriter.readline` একটি coroutine যা বাইট (bytes) রিটার্ন করে।
8. যদি কোনো বাইট পাওয়া না যায়, তবে এর অর্থ ক্লায়েন্ট কানেকশন বন্ধ করে দিয়েছে, তাই লুপ থেকে বের হয়ে যেতে হবে।
9. ডিফল্ট UTF-8 এনকোডিং ব্যবহার করে বাইটগুলোকে স্ট্রিং-এ (`str`) ডিকোড করা হয়।
10. ব্যবহারকারী যখন টার্মিনালে Ctrl-C চাপেন এবং Telnet ক্লায়েন্ট কন্ট্রোল বাইট পাঠায়, তখন একটি `UnicodeDecodeError` ঘটতে পারে; সরলতার জন্য এমন পরিস্থিতিতে কুয়েরিটিকে একটি নাল ক্যারেক্টার (null character) দ্বারা প্রতিস্থাপন করা হয়।
11. সার্ভার কনসোলে কুয়েরিটি লগ করা হয়।
12. যদি একটি কন্ট্রোল বা নাল ক্যারেক্টার পাওয়া যায়, তবে লুপ থেকে প্রস্থান করা হয়।
13. প্রকৃত সার্চ বা অনুসন্ধানের কাজটি সম্পন্ন করা হয়; এর কোড পরবর্তী অংশে দেওয়া হয়েছে।
14. সার্ভার কনসোলে রেসপন্স বা প্রতিক্রিয়া লগ করা হয়।
15. `StreamWriter` বন্ধ করা হয়।
16. `StreamWriter` বন্ধ হওয়া পর্যন্ত অপেক্ষা করা হয়। `.close()` মেথডের ডকুমেন্টেশনে এটি করার সুপারিশ করা হয়েছে।
17. সার্ভার কনসোলে এই ক্লায়েন্টের সেশনের সমাপ্তি লগ করা হয়।

---

এই উদাহরণের শেষ অংশটি হলো `search` coroutine, যা Example 21-15-এ দেখানো হয়েছে।

### Example 21-15. tcp_mojifinder.py: search coroutine

```python
async def search(query: str, index: InvertedIndex, writer: asyncio.StreamWriter) -> int:
    chars = index.search(query)
    lines = (line.encode() + CRLF for line in format_results(chars))
    writer.writelines(lines)

    await writer.drain()

    status_line = f'{"─" * 66} {len(chars)} found'
    writer.write(status_line.encode() + CRLF)

    await writer.drain()

    return len(chars)

```

1. `search`-কে অবশ্যই একটি coroutine হতে হবে কারণ এটি একটি `StreamWriter`-এ `write` করে এবং এর `.drain()` coroutine মেথডটি ব্যবহার করা আবশ্যক।
2. ইনভার্টেড ইনডেক্সে কুয়েরি করা হয়।
3. এই জেনারেটর এক্সপ্রেশনটি (generator expression) ইউনিকোড কোডপয়েন্ট, প্রকৃত ক্যারেক্টার, এর নাম এবং একটি CRLF `sequence` সহ UTF-8 এ এনকোড করা বাইট স্ট্রিং তৈরি করবে (যেমন: `b'U+0039\t9\tDIGIT NINE\r\n'`)।
4. লাইনগুলো পাঠানো হয়। আশ্চর্যজনকভাবে, `writer.writelines` কোনো coroutine নয়।
5. তবে `writer.drain()` একটি coroutine। এখানে `await` ব্যবহার করতে ভুল করা যাবে না!
6. একটি স্ট্যাটাস লাইন তৈরি করে সেটি পাঠানো হয়।

---

### গুরুত্বপূর্ণ নোট

লক্ষ্যণীয় যে, `tcp_mojifinder.py`-তে সমস্ত নেটওয়ার্ক I/O বাইট আকারে সম্পন্ন হয়; নেটওয়ার্ক থেকে প্রাপ্ত বাইটগুলোকে ডিকোড করতে হয় এবং বাইরে পাঠানোর আগে স্ট্রিংগুলোকে এনকোড করতে হয়। পাইথন ৩-এ ডিফল্ট এনকোডিং হলো UTF-8, এবং এই উদাহরণের সমস্ত `encode` এবং `decode` কলে পরোক্ষভাবে এটিই ব্যবহার করা হয়েছে।

আরও মনে রাখা প্রয়োজন যে, কিছু I/O মেথড হলো coroutines এবং সেগুলোকে অবশ্যই `await` দিয়ে রান করতে হয়, যেখানে অন্যগুলো সাধারণ ফাংশন। উদাহরণস্বরূপ, `StreamWriter.write` একটি সাধারণ ফাংশন, কারণ এটি একটি বাফারে `write` করে। অন্যদিকে, `StreamWriter.drain`—যা বাফার ফ্লাশ করে এবং নেটওয়ার্ক I/O সম্পাদন করে—তা একটি coroutine, ঠিক যেমন `StreamReader.readline` একটি coroutine—তবে `StreamWriter.writelines` নয়! এই বইয়ের প্রথম সংস্করণ লেখার সময়, coroutine গুলোকে স্পষ্টভাবে চিহ্নিত করার মাধ্যমে `asyncio` API ডকুমেন্টেশন উন্নত করা হয়েছিল।

`tcp_mojifinder.py` কোডটি হাই-লেভেল `asyncio` Streams API এর সুবিধা গ্রহণ করে যা একটি তৈরি সার্ভার প্রদান করে, ফলে শুধুমাত্র একটি হ্যান্ডলার ফাংশন ইমপ্লিমেন্ট করলেই চলে, যা একটি সাধারণ `callback` বা coroutine হতে পারে। এছাড়া একটি লোয়ার-লেভেল Transports এবং Protocols API রয়েছে, যা Twisted ফ্রেমওয়ার্কের ট্রান্সপোর্ট এবং প্রোটোকল অ্যাবস্ট্রাকশন দ্বারা অনুপ্রাণিত। এই লোয়ার-লেভেল API দিয়ে ইমপ্লিমেন্ট করা TCP এবং UDP ইকো সার্ভার ও ক্লায়েন্টসহ আরও তথ্যের জন্য `asyncio` ডকুমেন্টেশন দেখা যেতে পারে।

"""