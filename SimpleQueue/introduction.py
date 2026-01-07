"""
SimpleQueue মূলত একটি First-In First-Out (FIFO) pipeline.

এর প্রধান 3 টি ফাংশন:
1. put(item): Queue-তে একটি Data রাখা।
2. get(): Queue থেকে একটি Data বের করে আনা। যদি Queue খালি থাকে, তবে এটি Data না আসা পর্যন্ত অপেক্ষা (block) করবে।
3. empty(): Queue খালি কি না তা জানার জন্য empty() method ব্যবহার করা হয়।
"""

from multiprocessing import SimpleQueue

q = SimpleQueue()

print(q)

q.put("Apple")
q.put("Orange")

print("Queue : ", q)
print(q.empty())

print(q.get())
print("Queue : ", q)

print(q.get())
print("Queue : ", q)


print(q.empty())

# print("Length : ", len(q))    # it create bug.

"""
SimpleQueue তৈরি করা হয়েছে মূলত বিভিন্ন প্রসেসের মধ্যে ডেটা আদান-প্রদান করার জন্য। যখন একাধিক প্রসেস একই Queue ব্যবহার করে, তখন Queue-এর 
সাইজ বা দৈর্ঘ্য খুব দ্রুত পরিবর্তন হয়।

Race Condition: ধরুন এক মুহূর্তে len(q) call করা হলো এবং উত্তর এলো 5। কিন্তু ঠিক পরের মিলিসেকেন্ডেই অন্য একটি প্রসেস ওই Queue থেকে একটি 
ডেটা নিয়ে নিল। এখন আপনার কাছে থাকা 5 সংখ্যাটি ভুল। মাল্টিপ্রসেসিংয়ের ক্ষেত্রে এই ধরনের ভুল তথ্য বড় ধরনের Bug তৈরি করতে পারে।

Design Objectives: SimpleQueue কে যতটা সম্ভব "Simple" এবং দ্রুত রাখার জন্য এতে অতিরিক্ত ফিচার (like length গণনা করা) Add করা হয়নি।
"""
