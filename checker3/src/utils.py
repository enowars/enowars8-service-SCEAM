from httpx import AsyncClient
import string
import random
from bs4 import BeautifulSoup
from PIL import Image
import io
from logging import LoggerAdapter
from enochecker3 import MumbleException


def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


class InteractionManager:
    def __init__(self, address: str, logger: LoggerAdapter, email_name_key: dict = None) -> None:
        self.logger = logger
        self.logger.info(f"Creating InteractionManager with {address}")
        if email_name_key:
            self.logger.info(f"Using email_name_key: {email_name_key}")
            self.email = email_name_key['email']
            self.name = email_name_key['name']
            self.key = email_name_key['key']
        else:
            self.email, self.name, self.key = ("", "", "")
        self.address = address
        self.client = AsyncClient()

    async def register(self, vendor_lock: bool = False, low_quality: bool = False):
        self.name = generate_random_string(10)
        self.email = self.name + "@" + generate_random_string(10) + ".scam"
        data = {'email': self.email, 'name': self.name}
        if vendor_lock:
            data['vendor_lock'] = 'on'

        if low_quality:
            data['never_full'] = 'on'

        self.logger.info(f"Registering with {data}")
        try:
            r = await self.client.post(self.address + 'sign-up', data=data)
        except Exception as e:
            self.logger.error(f"Error registering: {data}")
            raise MumbleException("Error registering")
        try:
            r = await self.client.post(self.address + 'download_key')
        except Exception as e:
            self.logger.error(f"Error downloading key {data}")
            raise MumbleException("Error downloading key")
        self.key = r.content
        self.logger.info(f"Registration Key: {r.content}")
        return r.content

    async def login(self):
        data = {'email': self.email, 'private_key': self.key}
        self.logger.info(f"Logging in with {data}")
        try:
            r = await self.client.post(self.address + 'login', data=data)
        except Exception as e:
            self.logger.error(f"Error logging in: {data}")
            raise MumbleException("Error logging in")
        return r

    async def upload_image(self, image: bytes):
        files = {'file': image}
        self.logger.info(f"Uploading image")
        try:
            r = await self.client.post(self.address + 'profile_' + self.email, files=files)
        except Exception as e:
            self.logger.error(f"Error uploading image {self.email}")
            raise MumbleException("Error uploading image")
        return r

    async def download_profile_images(self):
        self.logger.info(f"Downloading profile")
        r = await self.client.get(self.address + 'profile_' + self.email)
        soup = BeautifulSoup(r.text, 'html.parser')
        imgs = soup.find_all('img')
        imgs = [img['src'] for img in imgs]
        self.logger.info(f"Found images: {imgs}")
        for index, e in enumerate(imgs):
            try:
                r = await self.client.get(self.address + e)
            except Exception as e:
                self.logger.error(f"Error downloading image {e}")
                raise MumbleException("Error downloading image")
            imgs[index] = Image.open(io.BytesIO(r.content))
        self.logger.info(f"Images decoded")
        return imgs

    def dump_info(self):
        self.logger.info(
            f"Dumping info: {self.email}, {self.name}, {self.key}")
        return {'email': self.email, 'name': self.name, 'key': self.key}
