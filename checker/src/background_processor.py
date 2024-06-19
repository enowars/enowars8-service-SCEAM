import os
from PIL import Image
from PIL import ImageOps
import segno
from segno import consts
import random
import string
from tqdm import tqdm

SCALE = 12
BORDER = 20

# Pathing
orginal_images_folder = os.path.dirname(os.path.realpath(__file__))
background_folder = os.path.join(orginal_images_folder, 'backgrounds_org')
processed_backgrounds_folder = os.path.join(
    orginal_images_folder, 'backgrounds')


os.makedirs(processed_backgrounds_folder, exist_ok=True)
if len(os.listdir(processed_backgrounds_folder)) != 0:
    quit()
# init dummy qr code to use as mask and other constants
flag = 'ENO'+''.join(random.choices(string.ascii_letters +
                     string.digits + '\/=', k=48))
qr = segno.make_qr(flag, error='L', boost_error=False, version=4)
qr_size = qr.symbol_size(scale=SCALE, border=BORDER)
keep_modules = (consts.TYPE_FINDER_PATTERN_DARK, consts.TYPE_FINDER_PATTERN_LIGHT, consts.TYPE_SEPARATOR,
                consts.TYPE_ALIGNMENT_PATTERN_DARK, consts.TYPE_ALIGNMENT_PATTERN_LIGHT, consts.TYPE_TIMING_DARK,
                consts.TYPE_TIMING_LIGHT)
border_offset = BORDER * SCALE
d = SCALE // 3

all_image_paths = os.listdir(background_folder)
for image_path in tqdm(all_image_paths):
    # open image
    image = Image.open(os.path.join(background_folder, image_path))
    # upscale image to qr code size
    image = ImageOps.contain(image, qr_size)
    # make into box
    box_image = Image.new('RGB', qr_size, (255, 255, 255))
    paste_x = (qr_size[0] - image.size[0]) // 2
    paste_y = (qr_size[1] - image.size[1]) // 2
    box_image.paste(image, (paste_x, paste_y))
    box_image = box_image.convert('RGBA')
    # add holes to box image
    for i, row in enumerate(qr.matrix_iter(scale=SCALE, border=BORDER, verbose=True)):
        for j, m in enumerate(row):
            # if qr_code keep_modules goes here make it transparent
            if m in keep_modules:
                box_image.putpixel((i, j), (0, 0, 0, 0))
            # if in qr code and not in border
            if (i > border_offset and j > border_offset) and (i < qr_size[0] - border_offset and j < qr_size[1] - border_offset):
                if (((i // d) % 3 == 1) and ((j // d) % 3 == 1)):
                    box_image.putpixel((i, j), (0, 0, 0, 0))
    pure_name = image_path.split('.')
    pure_name.pop(-1)
    pure_name = '.'.join(pure_name)
    box_image.save(os.path.join(
        processed_backgrounds_folder, pure_name+".png"), format='PNG')
