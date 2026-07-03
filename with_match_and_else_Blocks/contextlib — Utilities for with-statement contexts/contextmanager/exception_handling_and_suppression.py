from contextlib import contextmanager

@contextmanager
def ignore_specific_exception(exception_type):
    print('Context Entering....')

    try:
        yield
    except exception_type as e:
        print(f"Caught and suppressed expected exception: {type(e).__name__}")
    except Exception as e:
        print(f"Unexpected exception occurred: {type(e).__name__}. Reraising...")
        raise
    finally:
        print('Context Existing')


# Case-A
with ignore_specific_exception(ZeroDivisionError):
    print('Performing Division....')
    result = 10 / 0

# Case-B
try:
    with ignore_specific_exception(ZeroDivisionError):
        print('Accessing Invalid List Index.....')
        my_list = [1, 2, 3]
        invalid_item = my_list[5]
except IndexError:
    print("IndexError was reraised and caught outside the context manager.")

"""
- Case A: block এর ভেতর ZeroDivisionError ঘটলে তা generator এর except exception_type block এ ধরা পড়ে। যেহেতু এখানে নতুন করে কোনো error 
raise করা হয়নি, তাই পাইথন ধরে নেয় এটি handle হয়ে গেছে এবং মূল প্রোগ্রাম ক্র্যাশ না করে স্বাভাবিকভাবে চলতে থাকে।

- Case B: block এর ভেতর IndexError ঘটেছে, যা আমাদের নির্দিষ্ট করা exception এর বাইরে। তাই দ্বিতীয় except Exception block টি এটিকে ধরে এবং raise 
keyword এর মাধ্যমে পুনরায় বাইরে পাঠিয়ে দেয়। তবে error বাইরে পাঠানোর আগেও finally block টি execute হতে ভুল করে না।
"""
