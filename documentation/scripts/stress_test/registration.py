import random
from requests import Session
import string
import threading
import time
from httpx import AsyncClient
import asyncio

address = "http://localhost:8008/"
THREADS = 100


def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        diff = time2-time1
        print(f'{f.__name__} took {diff:.2f} s')
        print(f'{f.__name__} took {diff/THREADS:.5f} s per thread')
        return ret
    return wrap


def generate_random_string(length):
    return ''.join(
        random.choices(
            string.ascii_letters +
            string.digits,
            k=length))


def generate_random_data(length):
    name = generate_random_string(length)
    email = name + "@" + generate_random_string(length) + ".scam"
    data = {'email': email, 'name': name}
    data['vendor_lock'] = 'on'
    data['never_full'] = 'on'
    return data


def register_sessions():
    data = generate_random_data(10)
    client = Session()
    try:
        r = client.post(address + 'sign-up', data=data)
        r = client.post(address + 'download_key')
    except:
        print("registration failed")
    key = r.content
    return key


async def register_asyncClient():
    data = generate_random_data(10)
    client = AsyncClient()
    r = None
    try:
        while r is None:
            r = await client.post(address + 'sign-up', data=data)
        r = None
        while r is None:
            r = await client.post(address + 'download_key')
    except:
        print("registration failed")
    if not r:
        print("response is None")
        return None
    key = r.content
    return key


@timing
def stress_sessions():
    threads = []
    for _ in range(THREADS):
        threads.append(threading.Thread(target=register_sessions))
    for t in threads:
        t.start()
    for t in threads:
        t.join()


@timing
def stress_asyncClient():
    threads = []
    for _ in range(THREADS):
        threads.append(threading.Thread(
            target=asyncio.run, args=(register_asyncClient(),)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()


# WARNING retryies infinite times
if __name__ == "__main__":
    stress_sessions()
    stress_asyncClient()
