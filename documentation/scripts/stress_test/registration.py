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


async def register_aioClient(session):
    data = generate_random_data(10)
    try:
        await session.post(address + 'sign-up', data=data)
    except aiohttp.ClientError as e:
        print(f"Request to sign up failed: {e}")

    try:
        await session.post(address + 'download_key')
    except aiohttp.ClientError as e:
        print(f"Request to download key failed: {e}")

    await session.close()


async def stress_aiohttp():
    tasks = []

    for _ in range(THREADS):
        session = aiohttp.ClientSession()
        tasks.append(register_aioClient(session))
    await asyncio.gather(*tasks)


@timing
def run_async_aiohttp():
    asyncio.run(stress_aiohttp())


async def register_asyncClient(client):

    data = generate_random_data(10)
    try:
        await client.post(address + 'sign-up', data=data)
    except Exception as e:
        print(f"Request to sign up failed: {e}")

    try:
        await client.post(address + 'download_key')
    except Exception as e:
        print(f"Request to download key failed: {e}")
    print("closing")
    await client.aclose()


async def stress_asyncClient():
    tasks = []

    for _ in range(THREADS):
        client = AsyncClient()
        print(len(tasks))
        tasks.append(register_asyncClient(client))
    await asyncio.gather(*tasks)


@timing
def run_async_asyncclient():
    asyncio.run(stress_asyncClient())


if __name__ == "__main__":
    stress_sessions()
    run_async_aiohttp()
    run_async_asyncclient()
