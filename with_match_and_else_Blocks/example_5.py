import sys
from contextlib import contextmanager

@contextmanager
def looking_glass():
    original_write = sys.stdout.write

    def reverse_write(text):
        original_write(text[::-1])

    sys.stdout.write = reverse_write
    yield 'Aubdur Rob Anik'
    sys.stdout.write = original_write

