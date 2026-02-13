import itertools
import time
from threading import Thread, Event
import math

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

def spin(msg: str, done: Event):
    print("thread-1")
    for char in itertools.cycle(r'\|/-'):
        status = f'\r{char} {msg}'
        print(status, end='', flush=True)

        if done.wait(0.1):
            break
    blanks = ' ' * len(status)
    print(f'\r{blanks}\r', end='')


def slow():
    # time.sleep(3)
    is_prime(5000111000222021)
    return 42

def supervisor():
    done = Event()

    spinner = Thread(target=spin, args=('thinking!', done))
    print(f'Spinner Object: {spinner}')

    spinner.start()

    result = slow()

    done.set()

    spinner.join()

    return result

def main():
    result = supervisor()
    print(f"Answer : {result}")

if __name__ == '__main__':
    main()


"""
First-Run : 
Spinner Object: <Thread(Thread-1 (spin), initial)>
thread-1Main-Thread

Answer : True


Second-Run :
Spinner Object: <Thread(Thread-1 (spin), initial)>
thread-1
\ thinking!Main-Thread
Answer : True
"""
