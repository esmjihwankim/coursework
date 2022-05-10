from skimage.io import imread, imshow
from skimage.transform import resize, rescale
import matplotlib.pyplot as plt

img = imread('x-ray.jpg')
img_rescaled = rescale(img, scale = (0.2, 0.2, 1))

plt.subplot(121), imshow(img)
plt.title('Original Image')

plt.subplot(122), imshow(img_rescaled)
plt.title('Rescaled Image')
plt.show()