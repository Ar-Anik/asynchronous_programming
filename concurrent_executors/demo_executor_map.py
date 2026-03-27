from time import sleep, strftime
from concurrent.futures import ThreadPoolExecutor

def display(*args):
    print(strftime('[%H:%M:%S]'), end=' ')
    print(*args)


def loiter(n):
    msg = '{}loiter({}) : doing nothing for {}s....'
    display(msg.format('\t'*n, n, n))

    sleep(n)

    msg = '{}loiter({}): done.'
    display(msg.format('\t'*n, n))

    return n*10


def main():
    display('Script Starting.')

    executor = ThreadPoolExecutor(max_workers=5)
    results = executor.map(loiter, range(5))

    display('results : ', results)

    display('Waiting for individual results:')
    for i, results in enumerate(results):
        display(f'result {i}: {results}')


if __name__ == '__main__':
    main()
