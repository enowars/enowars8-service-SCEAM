import segno
import os
import random
import io
from pyzbar.pyzbar import decode
from PIL import Image
import numpy as np
import cv2
from segno import consts
import string
from qreader import QReader

RETRIES = 3
SCALE = 12
BORDER = 10
background_folder = os.path.join(os.path.dirname(__file__), "backgrounds")
qrReader = QReader()


def preload():
    # preload backgrounds
    res = []
    background_files = os.listdir(background_folder)
    for background_file in background_files:
        path = os.path.join(background_folder, background_file)
        res.append(cv2.imread(path))

    # preload mask by emulating one holing process
    flag = 'ENO'+''.join(random.choices(string.ascii_letters +
                                        string.digits + '\/=', k=48))
    qr = segno.make_qr(flag, error='L', boost_error=False, version=4)
    qr_size = qr.symbol_size(scale=SCALE, border=BORDER)
    keep_modules = (consts.TYPE_FINDER_PATTERN_DARK, consts.TYPE_FINDER_PATTERN_LIGHT, consts.TYPE_SEPARATOR,
                    consts.TYPE_ALIGNMENT_PATTERN_DARK, consts.TYPE_ALIGNMENT_PATTERN_LIGHT, consts.TYPE_TIMING_DARK,
                    consts.TYPE_TIMING_LIGHT)
    border_offset = BORDER * SCALE
    d = SCALE // 3
    qr_size_small = qr.symbol_size(scale=SCALE, border=0)
    mask_image = np.zeros((qr_size_small[1], qr_size_small[0]), dtype=np.uint8)
    for i, row in enumerate(qr.matrix_iter(scale=SCALE, border=BORDER, verbose=True)):
        for j, m in enumerate(row):
            # if qr_code keep_modules goes here make it transparent
            if m in keep_modules:
                mask_image[j-border_offset, i-border_offset] = 255
            # if in qr code and not in border
            if (i > border_offset and j > border_offset) and (i < qr_size[0] - border_offset and j < qr_size[1] - border_offset):
                if (((i // d) % 3 == 1) and ((j // d) % 3 == 1)):
                    mask_image[j-border_offset, i-border_offset] = 255
    mask_image = cv2.copyMakeBorder(mask_image, border_offset, border_offset,
                                    border_offset, border_offset, cv2.BORDER_CONSTANT, value=[0, 0, 0])

    return res, mask_image


preloaded_backgrounds, preloaded_mask = preload()


def create_qr_code(flag, scale=SCALE, border=BORDER) -> bytes:
    border_offset = border * scale
    qr = segno.make_qr(flag, error='L', boost_error=False, version=4)
    decoded = None
    qr_image = None
    final_image = random.choice(preloaded_backgrounds).copy()
    output = io.BytesIO()
    qr.save(output, kind='png', scale=scale, border=0)
    # Reset the pointer to the beginning of the BytesIO object
    output.seek(0)
    qr_image = Image.open(output).convert('RGB')
    qr_image = np.array(qr_image)
    qr_image = cv2.copyMakeBorder(qr_image, border_offset, border_offset,
                                  border_offset, border_offset, cv2.BORDER_CONSTANT, value=[255, 255, 255])
    heatmap = preloaded_mask == 255
    final_image[heatmap] = qr_image[heatmap]
    output = io.BytesIO()
    _, encoded_image = cv2.imencode('.png', final_image)
    output.write(encoded_image.tobytes())
    output.seek(0)
    res = output.getvalue()
    generated_img = Image.open(io.BytesIO(res))
    decoded = read_qr_code(generated_img)
    if decoded != flag:
        output = io.BytesIO()
        qr.save(output, kind='png', scale=3, border=border)
        output.seek(0)
        res = output.getvalue()
    return res


def read_qr_code(image: Image) -> str:
    qr_data = decode(image)
    if not qr_data:
        qr_data = qrReader.detect_and_decode(image)
        print("pyzbar failed")
        if not qr_data:
            return None
        return qr_data[0]
    return qr_data[0].data.decode('utf-8')


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
    # image.show()
    dec = read_qr_code(image)
    print(dec)
