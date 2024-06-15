import string
import random
from bs4 import BeautifulSoup
from PIL import Image
import io
from logging import LoggerAdapter
from enochecker3 import MumbleException, OfflineException
from requests import Session
from httpx import AsyncClient

success_login = "Logged in successfully!"
retry = 5


def generate_random_string(length):
    return ''.join(
        random.choices(
            string.ascii_letters +
            string.digits,
            k=length))


class InteractionManager:
    def __init__(
            self,
            address: str,
            logger: LoggerAdapter,
            forced_name: str = None,
            email_name_key: dict = None) -> None:
        self.logger = logger
        self.logger.info(f"Creating InteractionManager with {address}")
        if email_name_key:
            self.logger.info(f"Using email_name_key: {email_name_key}")
            self.email = email_name_key['email']
            self.name = email_name_key['name']
            self.key = email_name_key['key']
        else:
            self.email, self.name, self.key = ("", "", "")
        self.forced_name = forced_name
        self.address = address
        self.client = AsyncClient()

    async def ping(self):
        r = await self.client.get(self.address+"page_1", follow_redirects=True)
        if r.status_code != 200:
            raise OfflineException("Error pinging")

    async def register(
            self,
            vendor_lock: bool = False,
            low_quality: bool = False):
        self.name = generate_random_string(
            10) if not self.forced_name else self.forced_name
        self.email = self.name + "@" + generate_random_string(10) + ".scam"
        data = {'email': self.email, 'name': self.name}
        if vendor_lock:
            data['vendor_lock'] = 'on'

        if low_quality:
            data['never_full'] = 'on'

        self.logger.info(f"Registering with {data}")
        try:
            for i in range(retry):
                try:
                    r = await self.client.post(self.address + 'sign-up', data=data)
                    break
                except:
                    self.logger.info(f"Retrying registration {i}")
        except Exception as e:
            self.logger.error(
                f"Error registering: {data} ip: {self.address + 'sign-up'}, error: {e}")
            raise MumbleException("Error registering")
        try:
            for i in range(retry):
                try:
                    r = await self.client.post(self.address + 'download_key')
                    break
                except:
                    self.logger.info(f"Retrying key download {i}")
        except Exception as e:
            self.logger.error(
                f"Error downloading key {data}, ip: {self.address + 'download_key'}, error: {e}")
            raise MumbleException("Error downloading key")
        self.key = r.content
        self.logger.info(f"Registration Key: {r.content}")
        return r.content

    async def login(self):
        data = {'email': self.email, 'name': self.name}
        files = {'file': self.key}
        self.logger.info(f"Logging in with {data} and {files}")
        try:
            for i in range(retry):
                try:
                    r = await self.client.post(
                        self.address + 'login',
                        data=data,
                        files=files,
                        follow_redirects=True)
                    self.logger.info(f"Login response: {r.content.decode()}")
                    break
                except:
                    self.logger.info(f"Retrying login {i}")
        except Exception as e:
            self.logger.error(
                f"Error logging in: {data}, ip: {self.address + 'login'}, error: {e}")
            if success_login not in r.content.decode():
                raise MumbleException("Error logging in, invalid credentials")
            raise MumbleException("Error logging in response invalid")
        return r

    async def upload_image(self, image: bytes):
        files = {'file': image}
        self.logger.info(
            f"Uploading image to profile: {self.email} flag: {image}")
        try:
            for i in range(retry):
                try:
                    r = await self.client.post(
                        self.address + 'profile_' + self.email, files=files)
                    break
                except:
                    self.logger.info(f"Retrying image upload {i}")
        except Exception as e:
            self.logger.error(
                f"Error uploading image {self.email}, ip: {self.address + 'profile_' + self.email}, error: {e}")
            raise MumbleException("Error uploading image")
        return

    async def download_profile_images_from_self(self):
        return await self.download_profile_images_from_email(self.email)

    async def download_profile_images_from_email(self, email):
        imgs = await self.get_profile_image_urls(email)
        for index, e in enumerate(imgs):
            try:
                for i in range(retry):
                    try:
                        r = await self.client.get(self.address + e)
                        break
                    except:
                        self.logger.info(f"Retrying image download {i}")

            except Exception as e:
                self.logger.error(
                    f"Error downloading image {e}, ip: {self.address}, error: {e}")
                raise MumbleException("Error downloading image")
            imgs[index] = Image.open(io.BytesIO(r.content))
        self.logger.info(f"Images decoded {imgs}")

        return imgs

    async def get_profile_image_urls(self, email):
        self.logger.info(
            f"Downloading profile of {email}, url: {self.address + 'profile_' + email}")
        try:
            for i in range(retry):
                try:
                    r = await self.client.get(self.address + 'profile_' +
                                              email, follow_redirects=True)
                    break
                except:
                    self.logger.info(f"Retrying profile download {i}")

        except Exception as e:
            self.logger.error(
                f"Error downloading profile {email}, ip: {self.address + 'profile_' + email}, error: {e}")
            raise MumbleException("Error downloading profile")
        self.logger.info(f"Profile downloaded: {r.content.decode()}")
        soup = BeautifulSoup(r.content.decode(), 'html.parser')
        imgs = soup.find_all('img')
        imgs = [img['src'] for img in imgs]
        imgs = [img for img in imgs if 'uploads/' in img]
        self.logger.info(f"Found images: {imgs}")
        return imgs

    async def export_image_url(
            self,
            url,
            algorithm=".key_cert_algorithm(pkcs12.PBES.PBESv1SHA1And3KeyTripleDESCBC)"):
        # algorithm = ".kdf_rounds(50000).key_cert_algorithm(pkcs12.PBES.PBESv1SHA1And3KeyTripleDESCBC).hmac_hash(hashes.SHA1())"
        # algorithm = ".key_cert_algorithm(pkcs12.PBES.PBESv1SHA1And3KeyTripleDESCBC)"
        password = generate_random_string(10)
        pure_img = url.split('/')[-1]
        data = {'encryption_algorithm': algorithm,
                'password': password, 'img': pure_img}
        file = {'private_key': self.key}
        self.logger.info(f"Exporting image {url} with {data}")
        try:
            for i in range(retry):
                try:
                    r = await self.client.post(self.address + 'export_' +
                                               pure_img, data=data, files=file)
                    self.logger.info(f"Export post response: {r.content}")
                    break
                except:
                    self.logger.info(f"Retrying export {i}")
        except Exception as e:
            self.logger.error(
                f"Error exporting image {url}, ip: {self.address + 'export'} , error: {e}")
            raise MumbleException("Error exporting image")

        try:
            for i in range(retry):
                try:
                    r = await self.client.get(self.address + '/download_image')
                    self.logger.info(f"Exported image response: {r.content}")
                    break
                except:
                    self.logger.info(f"Retrying download {i}")
        except:
            raise MumbleException("Error downloading exported image")

        try:
            Image.open(io.BytesIO(r.content))
        except:
            raise MumbleException("Error decoding exported image")

        return Image.open(io.BytesIO(r.content))

    def dump_info(self):
        self.logger.info(
            f"Dumping info: {self.email}, {self.name}, {self.key}")
        return {'email': self.email, 'name': self.name, 'key': self.key}

    async def get_home_page(self):
        self.logger.info("Getting home page")
        try:
            for i in range(retry):
                try:
                    r = await self.client.get(self.address, follow_redirects=True)
                    break
                except:
                    self.logger.info(f"Retrying home page {i}")
        except Exception as e:
            self.logger.error(
                f"Error getting home page {self.address} , error: {e}")
            raise MumbleException("Error getting home page")
        return r.content
