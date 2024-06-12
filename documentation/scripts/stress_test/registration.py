import random
from requests import Session
import string
import threading
import time

address = "http://localhost:8008/"
THREADS = 100

# timing decorator


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


def register():
    name = generate_random_string(20)
    email = name + "@" + generate_random_string(20) + ".scam"
    data = {'email': email, 'name': name}
    data['vendor_lock'] = 'on'
    data['never_full'] = 'on'

    client = Session()
    try:
        r = client.post(address + 'sign-up', data=data)

    except:
        print("registration failed")

    try:
        r = client.post(address + 'download_key')
    except:
        print("download key failed")

    key = r.content
    return key


@timing
def create_threads(threads):
    for i in range(THREADS):
        t = threading.Thread(target=register)
        threads.append(t)


@timing
def start_threads(threads):
    for t in threads:
        t.start()


@timing
def join_threads(threads):
    for t in threads:
        t.join()


@timing
def stress():
    threads = []
    create_threads(threads)
    start_threads(threads)
    join_threads(threads)


if __name__ == "__main__":
    stress()
