import random
import string
import threading
import time
import requests
import asyncio
from httpx import AsyncClient
import aiohttp

address = "http://localhost:8008/"
THREADS = 100


def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        diff = time2 - time1
        print(f'{f.__name__} took {diff:.2f} s')
        print(f'{f.__name__} took {diff/THREADS:.5f} s per thread')
        return ret
    return wrap


def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_data(length):
    name = generate_random_string(length)
    email = f"{name}@{generate_random_string(length)}.scam"
    data = {'email': email, 'name': name}
    data['vendor_lock'] = 'on'
    data['never_full'] = 'on'
    return data


def register_sessions():
    data = generate_random_data(10)
    client = requests.Session()
    try:
        client.post(address + 'sign-up', data=data)
        client.post(address + 'download_key')
    except Exception as e:
        print(f"registration failed {e}")


@timing
def stress_sessions():
    threads = []
    for _ in range(THREADS):
        threads.append(threading.Thread(target=register_sessions))
    for t in threads:
        t.start()
    for t in threads:
        t.join()


async def register_asyncClient(session, endpoint):
    data = generate_random_data(10)
    try:
        async with session.post(address + endpoint, data=data) as response:
            response_data = await response.text()
    except Exception as e:
        print(f"Request to {endpoint} failed: {e}")


async def stress_aiohttp():
    tasks = []
    async with aiohttp.ClientSession() as session:
        for _ in range(THREADS):
            tasks.append(register_asyncClient(session, 'sign-up'))
            tasks.append(register_asyncClient(session, 'download_key'))
        await asyncio.gather(*tasks)


@timing
def run_async_aiohttp():
    asyncio.run(stress_aiohttp())


async def stress_asyncClient():
    tasks = []
    async with AsyncClient() as client:
        for _ in range(THREADS):
            tasks.append(register_asyncClient(client, 'sign-up'))
            tasks.append(register_asyncClient(client, 'download_key'))
        await asyncio.gather(*tasks)


@timing
def run_async_asyncclient():
    asyncio.run(stress_asyncClient())


if __name__ == "__main__":
    stress_sessions()
    run_async_aiohttp()
    run_async_asyncclient()
