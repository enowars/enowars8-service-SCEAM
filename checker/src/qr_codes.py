import segno
import os
import random
import io
from pyzbar.pyzbar import decode
from PIL import Image
RETRIES = 10
background_folder = os.path.join(os.path.dirname(__file__), "backgrounds")


def get_random_background_path() -> str:
    background_files = os.listdir(background_folder)
    background_file = random.choice(background_files)
    return os.path.join(background_folder, background_file)


def create_qr_code(flag, scale=12, border=30) -> bytes:
    # version 3 to minimize the size of the QR code
    qr = segno.make_qr(flag, error='L', boost_error=False, version=4)
    output = io.BytesIO()
    decoded = None
    iters = 0
    qr_image = None
    while decoded != flag and iters < RETRIES:
        iters += 1
        try:
            background = get_random_background_path()
            print("Creating QR code with background", background)
            qr.save(output, kind='png', scale=scale, border=border)
            qr_image = Image.open(output)
            output = io.BytesIO()
            qr_image = qr_image.convert('RGBA')
            overlay = Image.open(background)
            qr_image.paste(overlay, (0, 0), overlay)
            qr_image.save(output, format='PNG')
            output.seek(0)
            res = output.getvalue()
            generated_img = Image.open(io.BytesIO(res))
            decoded = read_qr_code(generated_img)
        except Exception as e:
            print("Error creating QR code", e)
            pass
    if iters == RETRIES:
        qr.save(output, kind='png', scale=5)
        output.seek(0)
        res = output.getvalue()
    return res


def read_qr_code(image: Image) -> str:
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
