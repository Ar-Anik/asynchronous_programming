"""
Q : asyncio.Future কী?
-> asyncio.Future হলো একটি Low-level object যা মূলত একটি `future result`-এর প্রতিনিধিত্ব করে। সহজ কথায় এটি একটি ফাঁকা বক্স বা Promise, যা
নির্দেশ করে যে— "একটি কাজ বর্তমানে ব্যাকগ্রাউন্ডে চলছে, যার ফলাফল এখনও প্রস্তুত নয়, তবে ভবিষ্যতে কোনো এক সময়ে এই বক্সে ফলাফলটি জমা হবে।"

এটি নিজে কোনো কোড execute করে না। এর একমাত্র দায়িত্ব হলো কোনো Asynchronous অপারেশনের চূড়ান্ত ফলাফল বা exception-টি নিজের কাছে ধরে রাখা। একটি
Future অবজেক্টের 3 টি State থাকতে পারে:
    - PENDING: কাজটি এখনও শেষ হয়নি।
    - CANCELLED: কাজটি বাতিল করা হয়েছে।
    - FINISHED: কাজটি সফলভাবে শেষ হয়েছে এবং ফলাফল প্রস্তুত।

এটি মূলত library developer বা backend engine-এর জন্য তৈরি। OS যখন কোনো Database বা নেটওয়ার্কের কাজ শেষ করে, তখন সে এই Future Object-এর
ভেতরে result push করে এর state FINISHED Set করে দেয়।
"""

"""
Q : asyncio.Task কী?
-> asyncio.Task হলো asyncio.Future এর একটি subclass বা child classs (অর্থাৎ asyncio.Future হলো তার parent)। একটি টাস্কের কাজ হলো কোনো 
একটি করুটিনকে (যা async def দিয়ে তৈরি) নিজের ভেতরে Wrap করা এবং সেটিকে Event লুপের active schedule-এ যুক্ত করা, যাতে কোডটি রান হতে পারে।

- ফিউচার যেখানে শুধু ফলাফলের জন্য অপেক্ষা করে, Task সেখানে সক্রিয়ভাবে কোড চালায়। এটি করুটিনের ইটারেটরের উপর send(None) call করে কোডটিকে ধাপে ধাপে 
সামনের দিকে এগিয়ে নিয়ে যায়।

- পাইথনে একই সাথে একাধিক Asynchronous Task parallel or concurrently চালাতে চাইলে সেগুলোকে asyncio.create_task(coroutine) মেথডের মাধ্যমে 
টাস্কে রূপান্তর করতে হয়। টাস্কে রূপান্তর করা মাত্রই Event Loop সেটিকে তার কাজের তালিকায় catalog ভুক্ত করে নেয়।

- যেহেতু টাস্কটি ফিউচারের একটি child ক্লাস, তাই করুটিনের কোডটি যখন শেষ পর্যন্ত run হয়ে কোনো value return করে, তখন টাস্কটি স্বয়ংক্রিয়ভাবে সেই ভ্যালুটিকে 
নিজের Future বক্সে জমা করে নেয়।
"""

"""
Task = Future (State Manager) + Coroutine (The actual Python code to execute)
"""


"""
File Descriptor কী?

যখন একটি পাইথন প্রোগ্রাম OS-এর কাছে কোনো ফাইল ওপেন করতে, নেটওয়ার্ক সকেট তৈরি করতে, বা ডাটাবেজের সাথে কানেকশন স্থাপন করতে রিকোয়েস্ট পাঠায়, OS তখন তার মেমোরিতে সেই কানেকশন বা ডেটা স্ট্রিম ট্র্যাক করার জন্য একটি রেকর্ড তৈরি করে। পাইথন প্রোগ্রাম সরাসরি OS-এর ভেতরের সেই আসল রেকর্ড অ্যাক্সেস করতে পারে না।

OS তখন এই কানেকশনটিকে ইউনিকভাবে চেনার জন্য পাইথন প্রোগ্রামকে একটি সাধারণ পজিটিভ ইন্টিজার (positive integer) নম্বর রিটার্ন করে। এই পজিটিভ ইন্টিজার নম্বরটিকেই File Descriptor বলা হয়। সহজ কথায়, এটি OS-এর কাছে থাকা আসল রেকর্ডের একটি টোকেন বা আইডি। পাইথন যখনই ডাটাবেজ থেকে ডেটা পড়তে চায়, সে OS-কে বলে— "আমার File Descriptor নম্বর ৫ থেকে ডেটা দাও।" পাইথনের Asynchronous লাইব্রেরিগুলো ডাটাবেজ কানেকশন তৈরি করার সময় এই File Descriptor-টি OS থেকে সংগ্রহ করে নেয়।

Listening System কী?

একটি Asynchronous প্রোগ্রামে যখন একসাথে অনেকগুলো (যেমন ১০০০টি) ডাটাবেজ বা নেটওয়ার্ক কানেকশন সচল থাকে, তখন সেখানে ১০০০টি File Descriptor তৈরি হয়। পাইথনের পক্ষে প্রতি মিলিসেকেন্ডে এই ১০০০টি কানেকশন একটি একটি করে ঘুরে চেক করা অসম্ভব যে কোনটিতে ডেটা এসেছে। এই পদ্ধতিতে চেক করতে গেলে সিপিইউ (CPU)-এর প্রচুর ক্ষমতা অপচয় হয়।

এই সমস্যা সমাধানের জন্য OS Kernel নিজেই একটি বিল্ট-ইন হাই-পারফরম্যান্স মেকানিজম বা system প্রদান করে, যাকে I/O Multiplexing বা Listening System বলা হয়। বিভিন্ন OS-এ এর কারিগরি নাম ভিন্ন হয়ে থাকে:

Linux-এর জন্য এটি epoll

macOS-এর জন্য এটি kqueue

Windows-এর জন্য এটি IOCP

এর কাজ: Event Loop চালু হওয়ার পর সে এই OS-এর Listening System-কে কল করে সমস্ত File Descriptor-এর একটি তালিকা জমা দেয় এবং নির্দেশ দেয় এগুলোর ওপর নজর রাখার জন্য। যখনই কোনো একটি কানেকশনে ডেটা আসবে, কেবল তখনই যেন Event Loop-কে জাগানো হয়। যতক্ষণ কোনো ডেটা না আসে, ততক্ষণ পর্যন্ত Event Loop ঐ Listening System-এর ভেতরে পজ হয়ে অলস বসে থাকে। এর ফলে প্রোগ্রামে কোনো অপ্রয়োজনীয় CPU পাওয়ার অপচয় হয় না।
"""


"""
যখন একটি করুটিনকে asyncio.create_task()-এর মাধ্যমে event লুপে schedule করা হয় এবং তার ভেতরে কোনো নেটওয়ার্ক বা ফাইল storage I/O-এর জন্য 
await করা হয়, তখন ব্যাকগ্রাউন্ডে নিচের সুনির্দিষ্ট sequence-টি ঘটে:

Step-1: Task creation and first activation
asyncio.create_task(coroutine_object) এর মাধ্যমে যখন একটি Task তৈরি করা হয়, তখন Event Loop সেটিকে তার track list-এ যুক্ত করে। Event 
Loop প্রথম সুযোগেই এই Task-এর উপর internal জেনারেটর method send(None) call করে। এর ফলে করুটিনের ভেতরের লাইনের কোড execute হওয়া শুরু করে।

Step-2: Reaching the limit of low-level I/O or slow operations
করুটিনটি চলতে চলতে যখন কোনো Asynchronous লাইব্রেরির লাইনে পৌঁছায় (যেমন: Database query বা asyncio.sleep()), তখন সেই লাইব্রেরির low-level 
Driver OS কার্নেলের কাছে I/O অপারেশনের request পাঠায়। একই সাথে Driver-টি তাৎক্ষণিকভাবে একটি asyncio.Future object তৈরি করে, যার প্রাথমিক অবস্থা 
বা state থাকে PENDING। এই objectটি মূলত একটি খালি বক্সের মতো কাজ করে।

Step-3: Await mechanism and futures throwing upwards (yield)
যখন কোডে await future_object লাইনটি execute হয়, তখন পাইথনের await keyword-টি ফিউচারের ভেতরের __await__() মেথডকে call করে। এই মেথডটি 
PENDING ফিউচার object-টিকে উপরে থাকা Task-এর কাছে yield (বাইরে ছুঁড়ে) করে দেয়। এর ফলে করুটিনের ভেতরের execution সাময়িকভাবে pause হয়ে যায়।

Step-৪: Receiving Future objects and registering callbacks by Task
উপরে থাকা asyncio.Task objectটি নিচ থেকে আসা PENDING ফিউচারটিকে receive করে। ফিউচারটি পাওয়ার পর Task একটি অত্যন্ত গুরুত্বপূর্ণ internal logic 
check সম্পন্ন করে। সে দেখে যে এই ফিউচারটি এখনও সম্পূর্ণ হয়নি। তখন Task ফিউচারের একটি বিশেষ মেথড রান করায়:
        future.add_done_callback(task._wakeup)
এর মাধ্যমে ফিউচারের ভেতরে থাকা _callbacks নামক একটি internal তালিকায় Task নিজের _wakeup মেথডের রেফারেন্সটি write করে রেখে দেয়। এর মূল উদ্দেশ্য 
হলো— Task অবজেক্টটি ফিউচারকে নির্দেশ দিয়ে রাখে যে, যখনই OS থেকে ডেটা আসবে, তখন যেন এই মেথডটিকে ডেকে Task-কে জাগানো হয়।

Step-5: Handing control to the Event Loop
callback Register করার পর Task অবজেক্টটি নিজেকে pause করে এবং Event Loop-এর কাছে program-এর control ফিরিয়ে দেয়। Event Loop তখন তার 
ready queue থেকে অন্য কোনো Task নিয়ে তা execute করতে চলে যায়। এই সময় বর্তমান Task এবং করুটিনটি সম্পূর্ণ Sleeping অবস্থায় থাকে।

Step-6: End of background operations and OS notifications
....



Step-7: ফিউচারের স্টেট পরিবর্তন এবং কলব্যাক trigger হওয়া
set_result() মেথডটি কল হওয়া মাত্রই ফিউচারের ভেতরে দুটি অত্যন্ত গুরুত্বপূর্ণ পরিবর্তন automatic ভাবে ঘটে:

ফিউচারের স্টেট পরিবর্তিত হয়ে FINISHED হয় এবং ভেতরের _result ফিল্ডে OS থেকে আসা আসল ডেটা বা text জমা হয়।

ফিউচারটি তার _callbacks তালিকায় থাকা সেই task._wakeup মেথডটিকে trigger করে। এর ফলে _wakeup মেথডটি এই ঘুমন্ত Task-টিকে আবার Event Loop-এর রেডি কিউ (_ready queue)-তে ট্রান্সফার করে দেয়।

Step-8: Task-এর পুনরুজ্জীবন ও কোড সচল হওয়া
Event Loop তার পরবর্তী চক্রে বা ইটারেশনে রেডি কিউ থেকে ওই Task-টিকে তুলে নেয় এবং তার ওপর পুনরায় send(None) মেথড কল করে। এর ফলে থমকে যাওয়া করুটিনটি ঠিক await লাইনের পর থেকে ফিউচারের ভেতর জমা হওয়া আসল ডেটাসহ আবার সচল হয়ে ওঠে।
"""