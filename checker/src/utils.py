import string
import random
from bs4 import BeautifulSoup
from PIL import Image
import io
from logging import LoggerAdapter
from enochecker3 import MumbleException, OfflineException, ChainDB, InternalErrorException
from httpx import AsyncClient, ConnectTimeout, NetworkError, PoolTimeout, Response


success_login = "Logged in successfully!"


def generate_random_string(length):
    return ''.join(
        random.choices(
            string.ascii_letters +
            string.digits,
            k=length))


class InteractionManager:
    def __init__(
            self,
            db: ChainDB,
            logger: LoggerAdapter,
            client: AsyncClient,
            forced_name: str = None,
    ) -> None:
        self.db = db
        self.logger = logger
        self.client = client
        self.forced_name = forced_name
        self.email, self.name, self.key = ("", "", "")
        self.logger.info(f"Creating InteractionManager with {client.base_url}")

    async def load_db(self):
        try:
            d = await self.db.get("credentials")
            self.email = d['email']
            self.name = d['name']
            self.key = d['key']
        except Exception as e:
            self.better_RequestError("Error loading credentials", e)

    def better_RequestError(self, message, error=None):
        m = f"{message}: {str(error)} {type(error).__name__}"
        m += f" name: {self.name}, email: {self.email}, key: {self.key},"
        m += f" address: {self.client.base_url}"
        self.logger.error(m)
        if any(isinstance(error, e) for e in [ConnectTimeout, NetworkError, PoolTimeout]):
            raise OfflineException(f"{message}")
        else:
            raise MumbleException(f"{message}")

    def better_logger_info(self, message):
        m = f"{message}: name: {self.name}, email: {self.email}, key: {self.key},"
        m += f" address: {self.client.base_url}"
        self.logger.info(m)

    async def register(self, quality, vendor_lock=False):
        # generate data to register
        if self.forced_name:
            self.name = self.forced_name
        else:
            self.name = generate_random_string(10)
        self.email = self.name + "@" + generate_random_string(10) + ".scam"
        data = {'email': self.email, 'name': self.name}
        if vendor_lock:
            data['vendor_lock'] = 'on'

        data['quality'] = quality

        # register
        try:
            r = await self.client.post('/sign-up', data=data)
        except Exception as e:
            self.better_RequestError("Error registering", e)

        # download key
        try:
            r = await self.client.post('/download_key')
        except Exception as e:
            self.better_RequestError("Error downloading private key", e)
        # save key
        self.key = r.content
        self.better_logger_info("Registered")

    async def login(self):
        data = {'email': self.email, 'name': self.name}
        files = {'file': self.key}
        try:
            r = await self.client.post('/login', data=data, files=files, follow_redirects=True)
        except Exception as e:
            self.better_RequestError("Error logging in", e)
        # validate success
        if success_login not in r.content.decode():
            self.better_RequestError("Error logging in, wrong credentials")
        self.better_logger_info("Logged in")

    async def upload_image(self, image: bytes):
        files = {'file': image}
        try:
            await self.client.post('/profile_' + self.email, files=files)
        except Exception as e:
            self.better_RequestError("Error uploading image", e)
        self.better_logger_info("Uploaded image")

    async def download_profile_images_from_self(self):
        return await self.download_profile_images_from_email(self.email)

    async def download_profile_images_from_email(self, email):
        imgs = await self.get_profile_image_urls(email)
        for index, img_path in enumerate(imgs):
            try:
                r = await self.client.get(img_path)
                imgs[index] = Image.open(io.BytesIO(r.content))
            except Exception as e:
                self.better_RequestError("Error downloading image", e)

        self.better_logger_info(f"Downloaded {len(imgs)} images from {email}")
        return imgs

    async def get_profile_image_urls(self, email):
        try:
            r = await self.client.get('/profile_' + email)
        except Exception as e:
            self.better_RequestError("Error getting profile", e)
        try:
            soup = BeautifulSoup(r.content.decode(), 'html.parser')
            imgs = soup.find_all('img')
            imgs = [img['src'] for img in imgs]
            imgs = [img for img in imgs if 'uploads/' in img]
        except Exception as e:
            self.better_RequestError("Error decoding profile", e)
        if len(imgs) == 0:
            self.better_RequestError("No images found in profile")

        self.better_logger_info(f"Found images: {imgs}")
        return imgs

    async def export_image_url(self, url, algorithm=None):
        if algorithm is None:
            algorithm = ".key_cert_algorithm(pkcs12.PBES.PBESv1SHA1And3KeyTripleDESCBC)"
        # algorithm = ".kdf_rounds(50000).key_cert_algorithm(pkcs12.PBES.PBESv1SHA1And3KeyTripleDESCBC).hmac_hash(hashes.SHA1())"

        password = generate_random_string(10)
        pure_img = url.split('/')[-1]
        data = {'encryption_algorithm': algorithm,
                'password': password, 'img': pure_img}
        file = {'private_key': self.key}

        try:
            await self.client.post(f'/export_{pure_img}', data=data, files=file)
        except Exception as e:
            self.better_RequestError("Error exporting image", e)

        try:
            r = await self.client.get('/download_image')
        except Exception as e:
            self.better_RequestError("Error downloading exported image", e)

        try:
            r = Image.open(io.BytesIO(r.content))
        except Exception as e:
            self.better_RequestError("Error decoding exported image", e)

        self.better_logger_info("Exported image")
        return r

    async def get_home_page(self):
        try:
            r = await self.client.get("/", follow_redirects=True)
        except Exception as e:
            self.better_RequestError("Error getting home page", e)
        return r.content

    async def logout(self):
        try:
            await self.client.get('/logout')
            self.logger.info("Logged out")
        except Exception as e:
            self.better_RequestError("Error logging out", e)

    async def dump_info(self):
        d = {'email': self.email, 'name': self.name, 'key': self.key}
        try:
            await self.db.set("credentials", d)
        except Exception as e:
            self.logger.error(f"Error dumping info into db {e}")
            raise InternalErrorException("Error dumping info into db")
        return d
