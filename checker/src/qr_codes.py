import segno
import os
import random
import io
from pyzbar.pyzbar import decode
from PIL import Image

# TODO Logging

background_folder = os.path.join(os.path.dirname(__file__), "backgrounds")


def get_random_background_path() -> str:
    background_files = os.listdir(background_folder)
    background_file = random.choice(background_files)
    return os.path.join(background_folder, background_file)


# TODO check decodability
def create_qr_code(flag) -> bytes:
    scale = 10
    qr = segno.make_qr(flag, error='L', boost_error=False)
    output = io.BytesIO()
    # qr.save(output, kind='png', scale=scale)
    decoded = None
    iters = 0
    while decoded != flag and iters < 100:
        iters += 1
        try:
            background = get_random_background_path()
            qr.to_artistic(
                background=background,
                target=output,
                kind='png',
                scale=scale,

            )
            output.seek(0)
            res = output.getvalue()
            decoded = read_qr_code(Image.open(io.BytesIO(res)))
        except:
            print("Error creating QR code")
            pass
        # print(decoded)
    if iters == 100:
        qr.save(output, kind='png', scale=scale)
        output.seek(0)
        res = output.getvalue()
    return res


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


if __name__ == "__main__":
    import random
    import string
    # ENO[A-Za-z0-9+\/=]{48}
    flag = 'ENO'+''.join(random.choices(string.ascii_letters +
                                        string.digits + '\/=', k=48))
    qr = create_qr_code(flag)
    # get image resolution:
    image = Image.open(io.BytesIO(qr))
    print(image.size)
    image.show()
