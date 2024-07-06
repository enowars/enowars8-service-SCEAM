import aiohttp
import asyncio
import json
import os

# http://localhost:5001/scoreboard/scoreboard33020.json
target_url = "http://localhost:5001/scoreboard/scoreboard"
data_folder = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(data_folder, exist_ok=True)
found_files = os.listdir(data_folder)
batch_size = 10  # Number of files to download in each batch


async def download_scoreboard(session, n):
    if f"scoreboard{n}.json" in found_files:
        print(f"scoreboard{n}.json already exists")
        return True
    url = f"{target_url}{n}.json"
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            with open(os.path.join(data_folder, f"scoreboard{n}.json"), "w") as f:
                json.dump(data, f)
            print(f"Downloaded scoreboard{n}.json")
            return True
        else:
            print(f"Failed to download scoreboard{n}.json")
            return False


async def download_batch(session, start, end):
    tasks = [download_scoreboard(session, i) for i in range(start, end)]
    results = await asyncio.gather(*tasks)
    return all(results)


async def download_all_scoreboards(batch_size):
    async with aiohttp.ClientSession() as session:
        counter = 0
        while True:
            success = await download_batch(session, counter, counter + batch_size)
            if not success:
                break
            counter += batch_size

if __name__ == "__main__":
    asyncio.run(download_all_scoreboards(batch_size))
    print("Done!")
