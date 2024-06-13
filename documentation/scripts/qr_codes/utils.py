import os
import random


def get_local_folder():
    return os.path.dirname(os.path.realpath(__file__))


def get_random_background_path(background_folder) -> str:
    background_files = os.listdir(background_folder)
    background_file = random.choice(background_files)
    return os.path.join(background_folder, background_file)


def get_random_image(background_folder) -> bytes:
    path = get_random_background_path(background_folder)
    with open(path, 'rb') as f:
        data = f.read()
    return data
