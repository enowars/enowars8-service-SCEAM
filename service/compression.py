import os
from PIL import Image
import random
from matplotlib import pyplot as plt

FULL_PATH = os.path.dirname(os.path.abspath(__file__))
FULL_PATH = os.path.join(FULL_PATH, 'instance')
FULL_PATH = os.path.join(FULL_PATH, 'uploads')
FULL_PATH = os.path.join(FULL_PATH, 'full')


def get_random_image() -> Image:
    all_files = os.listdir(FULL_PATH)
    file = random.choice(all_files)
    return Image.open(os.path.join(FULL_PATH, file))

# pil compare PIL.Image.NEAREST (use nearest neighbour),
# PIL.Image.BILINEAR (linear interpolation),
# PIL.Image.BICUBIC (cubic spline interpolation)
# PIL.Image.LANCZOS


def compare_all():
    n = range(2, 6)
    # plot, ax = plt.subplots(n, 4, figsize=(20, 20))
    plot, ax = plt.subplots(n.stop - n.start, 4, figsize=(20, 20))
    img = get_random_image()
    algs = [Image.NEAREST, Image.BILINEAR, Image.BICUBIC, Image.LANCZOS]
    alg_names = ['NEAREST', 'BILINEAR', 'BICUBIC', 'LANCZOS']
    counter = 0
    for i in n:
        for j in algs:
            ax[counter // 4, counter % 4].imshow(
                img.resize((img.width//i, img.height//i), j))
            ax[counter // 4, counter % 4].axis('off')
            ax[counter // 4, counter % 4].set_title(
                f"Factor: {i}, Alg: {alg_names[counter % 4]}")
            counter += 1

    plt.show()


def compare_specific(n, alg, factor):
    plot, ax = plt.subplots(2, n, figsize=(20, 20))
    for i in range(n):
        img = get_random_image()
        ax[0, i].imshow(img)
        ax[1, i].imshow(img.resize(
            (img.width//factor, img.height//factor), alg))
        ax[1, i].axis('off')
        ax[1, i].set_title(f"Factor: {factor}, Alg: {alg}")

    plt.show()


if __name__ == "__main__":
    # compare_all()
    compare_specific(5, Image.NEAREST, 8)
