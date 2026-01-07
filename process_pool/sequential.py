from primes import is_prime, NUMBERS
from time import perf_counter
from typing import NamedTuple

# see Details NamedTuple in python_code folder
class Result(NamedTuple):
    prime: bool
    elapsed: float
"""
A NamedTuple is a way to create a small, lightweight "container" for data. Normally a standard tuple is accessed by 
index (like result[0]). However when using NamedTuple, the data can be accessed using names. In this code Result is 
a custom object that stores two pieces of information:
    - prime: Whether the number is prime (True or False).
    - elapsed: How long the calculation took (a decimal number).

Q : Why use it? 
-> It makes the code much easier to read. Instead of writing return (True, 0.001), the code returns 
Result(prime=True, elapsed=0.001). Later we can access the data using result.prime instead of result[0].
"""

"""
What is perf_counter()?
-> The perf_counter() function (short for Performance Counter) comes from Python’s time module.

It acts like a highly precise stopwatch. It does not tell us the current time of day (like 10:30 AM); instead it 
provides a "start point" in seconds.
"""

def check(n):
    t0 = perf_counter()
    prime = is_prime(n)

    return Result(prime, perf_counter() - t0)


def main():
    print(f'Checking {len(NUMBERS)} numbers sequentially : ')
    t0 = perf_counter()

    for n in NUMBERS:
        prime, elapsed = check(n)
        label = 'P' if prime else ''
        print(f'{n:16} {label} {elapsed: 9.6f}s')

    elapsed = perf_counter() - t0
    print(f'Total time: {elapsed:.2f}s')


if __name__ == '__main__':
    main()
