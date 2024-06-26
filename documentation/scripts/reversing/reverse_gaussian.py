import numpy as np
import cv2
from skimage import restoration

# Parameters
image_path = r'documentation\scripts\reversing\qr.jpg'  # Path to the input image
blur_sigma = 6  # Standard deviation for Gaussian kernel
kernel_size = 15  # Kernel size used for blurring

img = cv2.imread(image_path, cv2.IMREAD_COLOR)

# Generate Gaussian kernel using cv2.getGaussianKernel
kernel_1d = cv2.getGaussianKernel(kernel_size, blur_sigma)
kernel = np.outer(kernel_1d, kernel_1d.transpose())  # Convert to 2D kernel
print(kernel.shape)

# Apply Gaussian blur using filter2D
blurred_img = np.zeros_like(img, dtype=np.float32)
for i in range(3):
    blurred_img[:, :, i] = cv2.filter2D(img[:, :, i], -1, kernel)


# Convert image to float format for restoration process
blurred_img_float = blurred_img.astype(float) / 255.0

# Perform Richardson-Lucy deconvolution
restored_img = np.zeros_like(blurred_img_float)
for i in range(3):
    # restored_img[:, :, i] = restoration.richardson_lucy(
    #     blurred_img_float[:, :, i], kernel, num_iter=30)
    restored_img[:, :, i] = restoration.wiener(
        blurred_img_float[:, :, i], kernel, 0.01, clip=False)


# Clip the restored image to [0, 1] range
restored_img = np.clip(restored_img, 0, 1)

# Convert restored image back to uint8 format for display
restored_img = (restored_img * 255).astype(np.uint8)

cv2.imshow('Restored Image', restored_img)
cv2.imshow('Original Image', img)
cv2.imshow('Blurred Image', blurred_img.astype(np.uint8))
cv2.waitKey(0)
