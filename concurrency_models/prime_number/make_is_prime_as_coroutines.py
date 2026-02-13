import asyncio
import itertools
import math

async def is_prime(n):
    print("Prime Function Start")
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
        if i%100000 == 1:
            await asyncio.sleep(0)

    return True

async def spin(msg: str):
    print("Spin Function Start")
    for char in itertools.cycle(r'\|/-'):
        status = f'\r{char} {msg}'
        print(status, flush=True, end='')

        try:
            await asyncio.sleep(.1)
        except asyncio.CancelledError:
            break

    blanks = ' ' * len(status)
    print(f'\r{blanks}\r', end='')


async def slow():
    result = await is_prime(5000111000222021)
    return result


async def supervisor():
    spinner = asyncio.create_task(spin('thinking!'))
    print(f'Spinner Object: {spinner}')

    result = await slow()

    spinner.cancel()

    return result


def main():
    result = asyncio.run(supervisor())
    print(f'Answer : {result}')


if __name__ == '__main__':
    main()

