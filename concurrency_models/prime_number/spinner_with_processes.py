import itertools
import time
import math
from multiprocessing import Process, Event
from multiprocessing import synchronize


def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n%2 == 0:
        return False

    root = math.isqrt(n)
    for i in range(3, root+1, 2):
        if n%i == 0:
            return False

    return True


def spin(msg: str, done: synchronize.Event):
    for char in itertools.cycle(r'\|/-'):
        status = f'\r{char} {msg}'
        print(status, end='', flush=True)

        if done.wait(.1):
            break

    blanks = ' ' * len(status)
    print(f'\r{blanks}\r', end='')


def slow():
    # time.sleep(3)
    is_prime(5000111000222021)
    return 42


def supervisor():
    done = Event()

    spinner = Process(target=spin, args=('thinking!', done))
    print(f'Spinner Object: {spinner}')

    spinner.start()

    result = slow()

    done.set()

    spinner.join()

    return result


def main():
    result = supervisor()
    print(f'Answer : {result}')


if __name__ == '__main__':
    main()

