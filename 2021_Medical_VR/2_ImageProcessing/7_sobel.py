import matplotlib.pyplot as plt
from skimage.io import imread, imshow
from skimage.filters import sobel_v, sobel_h, sobel

image = imread('x-ray.jpg', as_gray=True)
image_sobel_h = sobel_h(image)
image_sobel_v = sobel_v(image)
image_sobel = sobel(image)

#plotting images
plt.subplot(221), imshow(image)
plt.title('Original Image')
plt.subplot(222), imshow(image_sobel)
plt.title('Sobel Filter')
plt.subplot(223), imshow(image_sobel_h)
plt.title('Horizontal Edge')
plt.subplot(224), imshow(image_sobel_v)
plt.title('Vertical Edge')

plt.show()