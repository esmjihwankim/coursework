from skimage.io import imread, imshow
from skimage import exposure
import matplotlib.pyplot as plt

image = imread('x-ray.jpg')
image_bright = exposure.adjust_gamma(image, gamma=0.5, gain=1)
image_dark = exposure.adjust_gamma(image, gamma=1.5, gain=1)

# plotting images
plt.subplot(131), imshow(image)
plt.title('Original Image')

plt.subplot(132), imshow(image_bright)
plt.title('Bright Image')

plt.subplot(133), imshow(image_dark)
plt.title('Dark Image')

plt.show()
