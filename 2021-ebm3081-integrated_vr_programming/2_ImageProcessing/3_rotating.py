from skimage.io import imread, imshow
from skimage.transform import resize, rescale, rotate
import matplotlib.pyplot as plt

img = imread('x-ray.jpg')
plt.subplot(121), imshow(img)
plt.title('Original Image')

img_rotated = rotate(img, angle=-30)
plt.subplot(122), imshow(img_rotated)
plt.title('Rotated Image')

plt.show()
