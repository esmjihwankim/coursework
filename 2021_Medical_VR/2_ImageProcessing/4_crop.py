from skimage.io import imread, imshow
from skimage.transform import resize, rescale, rotate
import matplotlib.pyplot as plt

img = imread('x-ray.jpg')
print(img.shape)

cropped = img[100:(img.shape[0]-100), 100:(img.shape[1]-100)]
print(cropped.shape)

plt.subplot(121), imshow(img)
plt.title('Original Image')
plt.subplot(122), imshow(cropped)
plt.title('Cropped Image')

plt.show()
