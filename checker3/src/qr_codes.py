import segno
import os
import random
import io
from pyzbar.pyzbar import decode
from PIL import Image
from logging import LoggerAdapter
from enochecker3 import MumbleException

# TODO Logging

background_folder = os.path.join(os.path.dirname(__file__), "backgrounds")


def get_random_background_path() -> str:
    background_files = os.listdir(background_folder)
    background_file = random.choice(background_files)
    return os.path.join(background_folder, background_file)


# TODO check decodability
def create_qr_code(flag) -> bytes:
    scale = 5
    qr = segno.make_qr(flag)
    output = io.BytesIO()
    qr.save(output, kind='png', scale=scale)
    # background = get_random_background_path()
    # qr = qr.to_artistic(
    #     background=background,
    #     target=output,
    #     kind='png',
    #     scale=scale,
    #     quiet_zone=True,
    # )
    output.seek(0)
    return output.getvalue()


def get_random_image() -> bytes:
    path = get_random_background_path()
    with open(path, 'rb') as f:
        data = f.read()

    return data


def read_qr_code(image: Image) -> str:
    # Open the GIF image using PIL

    # Loop through each frame of the possible GIF
    for frame in range(image.n_frames):
        # Seek to the current frame
        image.seek(frame)

        # Decode the QR code
        qr_data = decode(image)

        # If QR code is detected, return the decoded data
        if qr_data:
            return qr_data[0].data.decode('utf-8')

    return None
