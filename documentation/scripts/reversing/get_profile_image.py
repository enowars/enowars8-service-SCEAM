import requests
from PIL import Image
import random
import string
import io


def generate_random_string(length):
    return ''.join(
        random.choices(
            string.ascii_letters +
            string.digits,
            k=length))


base = "http://localhost:8008/"
s = requests.Session()
name = generate_random_string(10)
email = name + "@" + generate_random_string(10) + ".scam"
data = {'email': email, 'name': name, 'quality': 2}
s.post(base + "sign-up", data=data)
r = s.post(base + "download_key")
key = r.content
img = Image.open(r"documentation\scripts\dog.4821.jpg")
b = io.BytesIO()
img.save(b, format="PNG")
b.seek(0)
b = b.getvalue()
files = {'file': b}
data = {'is_profile': 'on', 'description': 'Look at my new ENOFT!'}
r = s.post(base + "profile_" + email, files=files, data=data)
files = {'file': key}
r = s.post(base + "pimage_" + email, files=files, allow_redirects=True)
b = io.BytesIO(r.content)
img = Image.open(b)
img.show()
