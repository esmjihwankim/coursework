from skimage.io import imread, imshow
from skimage.transform import resize
import matplotlib.pyplot as plt

img = imread('x-ray.jpg')
print(img.shape)

img_resized = resize(img, (300, 150))

plt.subplot(121), imshow(img)
plt.title('Original Image')
plt.subplot(122), imshow(img_resized)
plt.title('Resized Image')
plt.show()