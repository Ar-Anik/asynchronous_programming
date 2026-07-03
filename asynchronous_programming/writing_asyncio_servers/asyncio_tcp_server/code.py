"""
-> Program Run Command
1st Terminal :  python code.py

2nd Terminal : nc localhost 2222

-> Input in 2nd Terminal : cat face
-> Input in 2nd Terminal : fire
"""

"""
nc হলো Netcat (নেটক্যাট) নামক একটি অত্যন্ত পরিচিত এবং শক্তিশালী কমান্ড-লাইন টুলের সংক্ষিপ্ত রূপ। নেটওয়ার্কিংয়ের দুনিয়ায় একে "Swiss-army knife" বা সর্বগুণসম্পন্ন হাতিয়ার বলা হয়ে থাকে।

এর মূল কাজ হলো TCP বা UDP প্রোটোকল ব্যবহার করে নেটওয়ার্ক কানেকশনের মাধ্যমে ডেটা আদান-প্রদান (পড়া এবং লেখা) করা। বর্তমান প্রেক্ষাপটে, পাইথনে যে TCP সার্ভারটি তৈরি করা হয়েছে, তার কার্যকারিতা পরীক্ষা করার জন্য nc একটি সাধারণ এবং স্ট্যান্ডার্ড TCP ক্লায়েন্ট (Client) হিসেবে ভূমিকা পালন করছে। এটি সার্ভারে কুয়েরি পাঠাতে এবং সার্ভার থেকে আসা ফলাফল টার্মিনালে প্রদর্শন করতে সাহায্য করে।
"""

"""
Netcat (যা সংক্ষেপে nc নামে পরিচিত) হলো একটি অত্যন্ত শক্তিশালী এবং বহুমুখী নেটওয়ার্কিং ইউটিলিটি (utility) সফটওয়্যার। এটি কম্পিউটার নেটওয়ার্কের মাধ্যমে ডেটা আদান-প্রদান করার জন্য ব্যবহৃত হয়। নেটওয়ার্কিংয়ের জগতে এর কার্যকারিতা এবং বহুমুখী ব্যবহারের কারণে একে নেটওয়ার্কের "সুইস আর্মি নাইফ" (Swiss Army Knife) বা সর্বগুণসম্পন্ন হাতিয়ার বলা হয়।

এটি মূলত TCP (Transmission Control Protocol) এবং UDP (User Datagram Protocol) প্রোটোকল ব্যবহার করে নেটওয়ার্ক কানেকশনের মাধ্যমে ডেটা পড়া এবং write করার কাজ করে।

Netcat এর প্রধান কাজ এবং ব্যবহারসমূহ:
নেটওয়ার্ক কানেকশন টেস্ট এবং ডিবাগিং: কোনো নির্দিষ্ট আইপি অ্যাড্রেস এবং পোর্টে নেটওয়ার্ক কানেকশন সচল আছে কি না তা পরীক্ষা করার জন্য এটি ব্যবহৃত হয়।

পোর্ট স্ক্যানিং (Port Scanning): একটি টার্গেট কম্পিউটারে কোন কোন পোর্টগুলো খোলা (open) আছে এবং কোন কোন পোর্ট বন্ধ আছে, তা খুঁজে বের করার জন্য Netcat ব্যবহার করা যায়।

ক্লায়েন্ট এবং সার্ভার হিসেবে কাজ করা: Netcat একই সাথে একটি সাধারণ ক্লায়েন্ট (Client) অথবা একটি ব্যাকগ্রাউন্ড সার্ভার হিসেবে কাজ করতে পারে। যেমন—কোনো একটি পোর্টে কানেকশন গ্রহণের জন্য এটি লিসেন (listen) করে বসে থাকতে পারে, আবার অন্য কোনো সার্ভারে কানেক্ট করার জন্য ক্লায়েন্ট হিসেবে command পাঠিয়ে ডেটা আদান-প্রদান করতে পারে।

ফাইল ট্রান্সফার (File Transfer): নেটওয়ার্কের আওতাধীন দুটি কম্পিউটারের মধ্যে কোনো জটিল কনফিগারেশন ছাড়াই সরাসরি ফাইল আদান-প্রদান করার জন্য এটি অত্যন্ত উপযোগী।

ব্যানার গ্র্যাবিং (Banner Grabbing): কোনো একটি পোর্টে কোন ধরনের সার্ভিস বা সফটওয়্যার রান করছে (যেমন—কোন সংস্করণের ওয়েব সার্ভার বা এসএসএইচ চালু আছে) তা জানার জন্য নেটক্যাট ব্যবহার করে সেই সার্ভিসের ব্যানার বা পরিচিতি তথ্য সংগ্রহ করা যায়।

নেটক্যাট অত্যন্ত ছোট একটি টুল এবং এর কোনো জটিল গ্রাফিক্যাল ইন্টারফেস নেই। এটি সম্পূর্ণরূপে টার্মিনাল বা command-line এর মাধ্যমে পরিচালিত হয়। স্ক্রিপ্টিং বা অটোমেশনের ক্ষেত্রে পাইথন বা ব্যাশ (Bash) স্ক্রিপ্টের সাথে যুক্ত করে নেটওয়ার্কের বিভিন্ন জটিল টাস্ক execute করার জন্য এটি ডেভেলপার এবং system অ্যাডমিনিস্ট্রেটরদের first choice।
"""

"""
-> nc localhost 2222
এই পুরো command-টিকে ভেঙে বিশ্লেষণ করলে এর অর্থ দাঁড়ায় নিচের রূপ:

nc: এটি অপারেটিং system-কে Netcat নামক ক্লায়েন্ট প্রোগ্রামটি চালু করার নির্দেশ দেয়।

localhost: এটি হলো কানেকশন তৈরি করার লক্ষ্যবস্তু বা হোস্ট ঠিকানা (IP Address)। localhost বলতে সর্বদা নিজের কম্পিউটারকে (আইপি ঠিকানা: 127.0.0.1) বোঝায়। যেহেতু সার্ভারটি একই কম্পিউটারে ব্যাকগ্রাউন্ডে চলছে, তাই এই হোস্টনেম ব্যবহার করা হয়েছে।

2222: এটি হলো সুনির্দিষ্ট পোর্ট নম্বর (Port Number)। পাইথন কোডের সার্ভারটি নেটওয়ার্কের এই ২২২২ নম্বর পোর্টে কানেকশন গ্রহণ করার জন্য ওপেন হয়ে আছে।

সারমর্ম: এই command-টির মাধ্যমে কম্পিউটারকে বলা হচ্ছে— "আমার নিজের কম্পিউটারের ২২২২ পোর্টে যে TCP সার্ভারটি চালু আছে, Netcat ক্লায়েন্টের সাহায্যে তার সাথে একটি সরাসরি নেটওয়ার্ক কানেকশন স্থাপন করো।"
"""


import asyncio
import functools
import sys
from asyncio.trsock import TransportSocket
"""
asyncio.trsock হলো asyncio এর একটি internal মডিউল যা নেটওয়ার্ক ট্রান্সপোর্ট লেয়ারের সকেটের সাথে সরাসরি কাজ করে। অন্যদিকে TransportSocket হলো একটি টাইপ হিন্ট (type hint)। পাইথনে coding করার সময় স্ট্যাটিক টাইপ চেকিং নিশ্চিত করার জন্য টাইপ হিন্টিং ব্যবহার করা হয়। এখানে server.sockets থেকে যে সকেট অবজেক্টগুলো পাওয়া যায়, সেগুলোর সঠিক ডাটা টাইপ ডিক্লেয়ার করার জন্য TransportSocket ব্যবহার করা হয়েছে। এর ফলে টাইপ চেকার সফটওয়্যার সহজেই বুঝতে পারে যে এটি একটি সকেট object এবং কোডে কোনো ভুল থাকলে তা সনাক্ত করতে পারে।
"""

from typing import cast

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

CRLF = b'\r\n'
PROMPT = b'?>'

async def search(query: str, index: InvertedIndex, writer: asyncio.StreamWriter):
    chars = index.search(query)
    print(chars)

    lines = (line.encode() + CRLF for line in format_results(chars))

    writer.writelines(lines)
    await writer.drain()

    status_line = f'{"-" * 66} {len(chars)} found'
    writer.write(status_line.encode() + CRLF)
    await writer.drain()

    return len(chars)


async def finder(index: InvertedIndex, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    client = writer.get_extra_info('peername')

    while True:
        writer.write(PROMPT)
        await writer.drain()

        data = await reader.readline()

        if not data:
            break

        try:
            query = data.decode().strip()
        except UnicodeError:
            query = '\x00'

        print(f'From {client}: {query}')
        if query:
            if ord(query[:1]) < 32:
                break

            results = await search(query, index, writer)
            print(f'To {client}: {results} result')

    writer.close()
    await writer.wait_closed()

    print(f'Close {client}')

"""
-> asyncio.StreamReader এবং asyncio.StreamWriter
asyncio এর উচ্চ-স্তরের (high-level) স্ট্রীম API-তে এই দুটি অত্যন্ত গুরুত্বপূর্ণ object। নেটওয়ার্ক যোগাযোগের সময় ডেটা আদান-প্রদান সহজ করার জন্য এগুলো ব্যবহার করা হয়।

asyncio.StreamReader: এটি নেটওয়ার্ক থেকে আগত ডেটা পড়ার (read) জন্য ব্যবহৃত হয়। যখন কোনো ক্লায়েন্ট সার্ভারে কোনো তথ্য পাঠায়, তখন এই রিডারের মাধ্যমে সেই তথ্য লাইনের পর লাইন বা নির্দিষ্ট বাইট আকারে পড়া সম্ভব হয়।

asyncio.StreamWriter: এটি নেটওয়ার্কে ডেটা পাঠানোর বা লেখার (write) জন্য ব্যবহৃত হয়। সার্ভার যখন কোনো ক্লায়েন্টকে ডেটা ফেরত দিতে চায়, তখন এই রাইটারের সাহায্য নেওয়া হয়।
"""

"""
-> writer.get_extra_info('peername')
get_extra_info() হলো এমন একটি মেথড যার মাধ্যমে সকেটের নেটওয়ার্ক কানেকশন সংক্রান্ত বিভিন্ন অতিরিক্ত তথ্য সংগ্রহ করা যায়।

এখানে 'peername' প্যারামিটারটি ব্যবহার করার মাধ্যমে দূরবর্তী প্রান্তে সংযুক্ত থাকা ক্লায়েন্টের নেটওয়ার্ক ঠিকানা (IP address এবং Port number) একটি টাপল (tuple) আকারে পাওয়া যায়। নেটওয়ার্কিংয়ের ভাষায় peer বলতে অপর প্রান্তের কম্পিউটার বা নোডটিকে বোঝায়। সুতরাং, peername এর অর্থ হলো যে ক্লায়েন্টটি সার্ভারের সাথে যুক্ত হয়েছে, তার নিজস্ব আইপি এবং পোর্ট নম্বর।
"""

"""
-> asyncio.StreamWriter.write()
StreamWriter.write(): এটি একটি সাধারণ ফাংশন যা একটি একক বাইট স্ট্রিং (bytes) নিয়ে তা মেমোরির একটি internal buffer-এ জমা করে বা লেখে (write)। এটি কোনো coroutine নয়, তাই এই মেথডটি ব্যবহার করার সময় শুরুতে await ব্যবহার করার প্রয়োজন হয় না।
"""

"""
-> asyncio.StreamWriter.writelines()
StreamWriter.writelines(): এটি একটি ইটারেবল অবজেক্ট (যেমন বাইট স্ট্রিংয়ের লিস্ট বা জেনারেটর) থেকে একাধিক বাইট স্ট্রিং একসাথে নিয়ে internal buffer-এ লেখে (write)। এটিও কোনো coroutine নয়, তাই এর জন্যও await প্রয়োজন হয় না। এটি মূলত একবারে অনেকগুলো লাইন বা ডেটার টুকরো বাফারে জমা করার জন্য ব্যবহৃত হয়।
"""

"""
-> await writer.drain()
StreamWriter.write() বা writelines() মেথডগুলো যখন কোনো ডেটা লেখে, তখন তা সরাসরি নেটওয়ার্কের মাধ্যমে ক্লায়েন্টের কাছে চলে যায় না। ডেটাগুলো প্রথমে মেমোরির একটি internal buffer-এ জমা হয়।

StreamWriter.drain() হলো একটি coroutine যা সেই বাফারে জমা থাকা সমস্ত ডেটা ফ্লাশ (flush) করে এবং নেটওয়ার্ক সকেটের মাধ্যমে ক্লায়েন্টের কাছে পাঠিয়ে দেয়। যেহেতু নেটওয়ার্কে ডেটা পাঠানো একটি সময়সাপেক্ষ বিষয়, তাই এটি একটি নন-ব্লকিং অপারেশন নিশ্চিত করে এবং এটিকে সচল রাখার জন্য অবশ্যই এর আগে await ব্যবহার করতে হয়। এটি ব্যবহার না করলে বাফারের ডেটা আটকে থাকতে পারে এবং ক্লায়েন্ট সময়মতো রেসপন্স পাবে না।
"""

"""
-> if ord(query[:1]) < 32:
ord() ফাংশন: এটি পাইথনের একটি বিল্ট-ইন ফাংশন যা কোনো একটি একক ক্যারেক্টারের ইউনিকোর্ড কোডপয়েন্ট (একটি পূর্ণসংখ্যা বা integer মান) রিটার্ন করে। যেমন: ord('A') এর মান হলো ৬৫।

ord(query[:1]): এখানে query[:1] এর মাধ্যমে ক্লায়েন্টের পাঠানো text কুয়েরির একদম প্রথম ক্যারেক্টারটি আলাদা করে নেওয়া হয় (slicing)। এরপর ord(query[:1]) < 32 কোডের মাধ্যমে একটি logic check করা হয়। ইউনিকোড টেবিলে ৩২ এর চেয়ে কম মানের ক্যারেক্টারগুলো হলো বিভিন্ন অদৃশ্য কন্ট্রোল ক্যারেক্টার (যেমন: ব্যাকস্পেস, এন্টার, নাল ক্যারেক্টার ইত্যাদি)। যদি ক্লায়েন্ট এমন কোনো কন্ট্রোল ক্যারেক্টার পাঠায়, তবে সার্ভার বুঝে নেয় যে সেশনটি বন্ধ করার সময় হয়েছে এবং লুপটি ভেঙে (break) দেয়।
"""

"""
-> writer.close()
যখন ক্লায়েন্টের সাথে সমস্ত ডেটা আদান-প্রদান এবং যোগাযোগের কাজ পুরোপুরি শেষ হয়ে যায়, তখন সেশনটি বন্ধ করার জন্য StreamWriter.close() ব্যবহার করা হয়।

কখন ব্যবহার করা হয়: ক্লায়েন্ট কানেকশন বিচ্ছিন্ন করলে অথবা সার্ভার নিজে থেকে কানেকশন শেষ করতে চাইলে এটি ব্যবহার করা হয়।

এটি কি কাজ করে: এটি আন্ডারলাইং সকেট কানেকশনটি বন্ধ করার প্রক্রিয়া শুরু করে। এটি মেমোরি এবং নেটওয়ার্ক সকেটের রিসোর্সগুলো মুক্ত করে দেয় যেন system-এ কোনো রিসোর্স লিক না হয়।
"""

"""
-> await writer.wait_closed()
StreamWriter.close() মেথডটি কল করার সাথে সাথেই কানেকশনটি তাৎক্ষণিকভাবে এবং সম্পূর্ণভাবে বন্ধ হয়ে যায় না; এটি কেবল বন্ধ হওয়ার প্রক্রিয়াটি ব্যাকগ্রাউন্ডে শুরু করে।

await writer.wait_closed() হলো একটি coroutine যা সকেটটি সম্পূর্ণভাবে বন্ধ না হওয়া পর্যন্ত পরবর্তী কোড কার্যকর করা স্থগিত রাখে। এটি নিশ্চিত করে যে সকেট কানেকশনটি নিরাপদে এবং পুরোপুরি বন্ধ হয়েছে, যার ফলে প্রোগ্রামের পরবর্তী ধাপগুলো কোনো ত্রুটি ছাড়াই সম্পন্ন হতে পারে।
"""

async def supervisor(index: InvertedIndex, host: str, port: int):
    server = await asyncio.start_server(functools.partial(finder, index), host, port)
    socket_list = cast(tuple[TransportSocket, ...], server.sockets)

    addr = socket_list[0].getsockname()


    print(f'Serving on {addr}, Hit CTRL-C to Stop.')
    await server.serve_forever()

"""
-> await asyncio.start_server(functools.partial(finder, index), host, port)
সার্ভার হলো এমন একটি কেন্দ্রীয় প্রোগ্রাম বা system যা একটি নির্দিষ্ট নেটওয়ার্ক ঠিকানায় (IP এবং Port) সারাক্ষণ অপেক্ষা করে। যখনই দূরবর্তী কোনো কম্পিউটার বা ক্লায়েন্ট (যেমন Telnet বা কোনো ব্রাউজার) সেই ঠিকানায় যুক্ত হতে চায়, সার্ভার সেই কানেকশনটি গ্রহণ করে এবং ক্লায়েন্টের পাঠানো command বা অনুরোধ অনুযায়ী কাজ করে ফলাফল ফেরত পাঠায়।

asyncio.start_server: এটি একটি উচ্চ-স্তরের (high-level) ফাংশন যা ব্যাকগ্রাউন্ডে একটি TCP সকেট সার্ভার তৈরি করে এবং সেটিকে নির্দিষ্ট হোস্ট ও পোর্টে কানেকশন গ্রহণের জন্য চালু করে। নেটওয়ার্কিং কোড নিজে থেকে নতুন করে না লিখে খুব সহজে সেশন হ্যান্ডেল করার জন্য এটি ব্যবহার করা হয়।
"""

"""
-> socket_list = cast(tuple[TransportSocket, ...], server.sockets)
server.sockets: এটি হলো সার্ভার প্রোগ্রামের অধীনে সচল থাকা সমস্ত আন্ডারলাইং সকেট object-গুলোর একটি ইন্টারনাল লিস্ট বা কালেকশন। সার্ভার কোন কোন সকেটে লিসেন করছে তা এর মাধ্যমে জানা যায়।

... (Ellipsis) এর অর্থ: টাইপ হিন্টিং দেওয়ার সময় টাপলের ভেতরে ... ব্যবহার করার অর্থ হলো, এই টাপলটিতে যেকোনো সংখ্যক উপাদান থাকতে পারে (একটি, দুটি বা তার বেশি), তবে শর্ত হলো প্রতিটি উপাদানের ডাটা টাইপ অবশ্যই TransportSocket হতে হবে। এটি একটি পরিবর্তনশীল দৈর্ঘ্যের টাপল নির্দেশ করার স্ট্যান্ডার্ড নিয়ম। cast ফাংশনটির মাধ্যমে টাইপ চেকারকে নিশ্চিত করা হয় যেন সে এটিকে এই নির্দিষ্ট ফরম্যাটের টাপল হিসেবে গণ্য করে।
"""

"""
-> addr = socket_list[0].getsockname()
একটি সার্ভার এক বা একাধিক সকেট বা নেটওয়ার্ক ইন্টারফেসে ব্যাকগ্রাউন্ডে চালু থাকতে পারে। socket_list[0] এর মাধ্যমে সেই তালিকার প্রথম সকেট object-টিকে সুনির্দিষ্টভাবে নির্বাচন করা হয়।

এরপর সেই সকেটের ওপর getsockname() মেথডটি কল করলে ওই সকেটের নিজস্ব লোকাল আইপি অ্যাড্রেস এবং পোর্ট নম্বর একটি টাপল আকারে (যেমন: ('127.0.0.1', 2222)) রিটার্ন করে। এটি মূলত সার্ভারটি লোকাল কম্পিউটারের কোন আইপি এবং পোর্টে সফলভাবে সচল হয়েছে তা স্ক্রিনে প্রিন্ট করে দেখার জন্য ব্যবহার করা হয়।
"""

"""
-> await server.serve_forever()
serve_forever() হলো asyncio.Server ক্লাসের একটি গুরুত্বপূর্ণ coroutine মেথড।

এর কাজ: এটি সার্ভারটিকে চিরকাল বা অনির্দিষ্টকালের জন্য সচল রাখে এবং অবিরামভাবে নতুন নতুন ক্লায়েন্ট কানেকশন গ্রহণ করার প্রক্রিয়াটি চালু রাখে। যদি এই মেথডটির আগে await ব্যবহার করা না হতো, তবে supervisor ফাংশনটি তার কাজ শেষ করে তাৎক্ষণিকভাবে রিটার্ন করত। এর ফলে মেইন ইভেন্ট লুপ বন্ধ হয়ে পুরো প্রোগ্রামটি সাথে সাথে বন্ধ হয়ে যেত। এটি ইভেন্ট লুপকে নির্দেশ দেয় যেন সার্ভারটি বন্ধ না করে ব্যাকগ্রাউন্ডে ক্লায়েন্টের অনুরোধের জন্য সবসময় প্রস্তুত রাখা হয়।
"""


def main(host: str = '127.0.0.1', port_arg: str = '2222'):
    port = int(port_arg)

    print('Building Index.')
    index = InvertedIndex()

    try:
        asyncio.run(supervisor(index, host, port))
    except KeyboardInterrupt:
        print('\nServer Shut Down.')


if __name__ == '__main__':
    main(*sys.argv[1:])
