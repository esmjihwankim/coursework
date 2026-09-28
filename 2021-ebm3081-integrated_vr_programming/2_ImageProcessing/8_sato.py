import matplotlib.pyplot as plt
from skimage.io import imread, imshow
from skimage.filters import sato

image = imread('x-ray.jpg', as_gray=True)
image_dog = imread('dog.jpg', as_gray=True)
image_sato_xr = sato(image, sigmas=6, black_ridges=True, mode='constant', cval=0)
image_sato_dog = sato(image_dog, sigmas=2, black_ridges=True, mode='constant', cval=0)

plt.subplot(121), imshow(image)
plt.title('Original Image - xray')

plt.subplot(122), imshow(image_sato_xr)
plt.title('Sato Image - xray')

plt.show()