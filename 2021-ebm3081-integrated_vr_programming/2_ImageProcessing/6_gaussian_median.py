import matplotlib.pyplot as plt
from skimage.io import imread, imshow
from skimage.filters import gaussian, median

image = imread('x-ray.jpg', as_gray=True)
image_gaussian = gaussian(image, sigma=5.5)
image_median = median(image)

#plotting images
plt.subplot(131), imshow(image)
plt.title('Original Image')

plt.subplot(132), imshow(image_gaussian)
plt.title('Gaussian Filter')

plt.subplot(133), imshow(image_median)
plt.title('Median Filter')

plt.show()
