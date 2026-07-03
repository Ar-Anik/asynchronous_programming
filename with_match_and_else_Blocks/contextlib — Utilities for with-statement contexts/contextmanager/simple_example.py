from contextlib import contextmanager

@contextmanager
def file_manager(filename, mode):
    print(f'Opening file: {filename}')
    file_obj = open(filename, mode)

    try:
        yield file_obj
    finally:
        print(f'Closing file: {filename}')
        file_obj.close()

with file_manager('test_file.txt', 'w') as f:
    f.write('Hello, For Contextlib!')
    print('Writing Process inside the block is complete.')

"""
- Resource Preparation: file_manager function টি কল করার সাথে সাথে file টি নির্দিষ্ট mode এ open হয় এবং yield এর মাধ্যমে file object টি as 
f এর f variable এ পাস করা হয়।
- Block Execution: with block এর ভেতরের কোড execute হয় এবং file এ টেক্সট লেখা হয়।
- Resource Release: block এর কাজ শেষ হওয়া মাত্রই কোডটি স্বয়ংক্রিয়ভাবে finally block এ চলে যায় এবং file টি close করে দেয়।
"""
