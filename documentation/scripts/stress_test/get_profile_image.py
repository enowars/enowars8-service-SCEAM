import httpx
from PIL import Image
import random
import string
import io
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
import logging

logger = logging.getLogger("Service Benchmark Logger")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("get_profile_image.log")
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)


def generate_random_string(length):
    return ''.join(
        random.choices(
            string.ascii_letters +
            string.digits,
            k=length))


async def task():
    base = "http://localhost:8008/"
    async with httpx.AsyncClient() as client:
        name = generate_random_string(10)
        email = name + "@" + generate_random_string(10) + ".scam"
        data = {'email': email, 'name': name, 'quality': 2}

        await client.post(base + "sign-up", data=data)

        r = await client.post(base + "download_key")
        key = r.content

        img = Image.open(r"documentation/scripts/stress_test/dog.4821.jpg")
        b = io.BytesIO()
        img.save(b, format="PNG")
        b.seek(0)
        b = b.getvalue()
        files = {'file': ('image.png', b, 'image/png')}
        data = {'is_profile': 'on', 'description': 'Look at my new ENOFT!'}

        await client.post(base + "profile_" + email, files=files, data=data)

        files = {'file': ('keyfile', key)}
        r = await client.post(base + "pimage_" + email, files=files, follow_redirects=True)

        b = io.BytesIO(r.content)
        img = Image.open(b)


async def main(n):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        tasks = [loop.run_in_executor(
            executor, asyncio.run, task()) for _ in range(n)]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    n = 50  # Number of times to execute the script concurrently
    t1 = time.time()
    asyncio.run(main(n))
    time_taken = time.time() - t1
    gunicorn_config_raw = None
    with open(r"service\gunicorn.conf.py", "r") as f:
        gunicorn_config_raw = f.read()

    logger.info(
        f"Time taken: {time_taken} for {n} repeat \n {gunicorn_config_raw}")
    print(f"Time taken: {time_taken}")
