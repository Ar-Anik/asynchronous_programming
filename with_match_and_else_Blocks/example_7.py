import sys
from contextlib import contextmanager

@contextmanager
def looking_glass():
    original_write = sys.stdout.write

    def reverse_write(text):
        original_write(text[::-1])

    sys.stdout.write = reverse_write
    msg = ''

    try:
        yield 'Aubdur Rob Anik'
    except ZeroDivisionError:
        msg = 'Please Do Not Divide By Zero'
    finally:
        sys.stdout.write = original_write
        if msg:
            print(msg)
