import numpy as np
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import pydicom
from skimage import morphology
from scipy import ndimage


# load and windowing image
def transform_to_hu(medical_image, image):
    intercept = medical_image.RescaleIntercept
    slope = medical_image.RescaleSlope
    hu_image = image * slope + intercept

    return hu_image


def load_hu_image(file_path):
    medical_image = pydicom.read_file(file_path)
    image = medical_image.pixel_array
    hu_image = transform_to_hu(medical_image, image)

    return hu_image


def window_image(image, window_center, window_width):
    img_min = window_center - window_width // 2
    img_max = window_center + window_width // 2
    window_image = image.copy()
    window_image[window_image < img_min] = img_min
    window_image[window_image > img_max] = img_max

    return window_image

def remove_noise(file_path, display=False):
    # remove noise pixel on left and right
    medical_image = pydicom.read_file(file_path)
    image = medical_image.pixel_array
    hu_image = transform_to_hu(medical_image, image)
    chest_image = window_image(hu_image, -600, 1500)

    segmentation = morphology.dilation(chest_image, np.ones((5, 5)))
    labels, label_nb = ndimage.label(segmentation)

    # improving images
    label_count = np.bincount(labels.ravel().astype(np.int))
    label_count[0] = 0
    mask = labels == label_count.argmax()
    mask = morphology.dilation(mask, np.ones((5, 5)))
    mask = ndimage.morphology.binary_fill_holes(mask)
    mask = morphology.dilation(mask, np.ones((3, 3)))

    masked_image = mask * chest_image

    if display:
        plt.figure(figsize=(15, 2.5))

        plt.subplot(141)
        plt.imshow(chest_image)
        plt.title('Original Image')
        plt.axis('off')

        plt.subplot(142)
        plt.imshow(mask)
        plt.title('Mask')
        plt.axis('off')

        plt.subplot(143)
        plt.imshow(masked_image)
        plt.title('Final Image')
        plt.axis('off')

        plt.show()

    return masked_image


def crop_image(image, display=False):
    mask = image == 0

    # find the brain area
    coords = np.array(np.nonzero(~mask))
    top_left = np.min(coords, axis=0)
    bottom_right = np.max(coords, axis=1)

    #remove the background
    cropped_image = image[top_left[0]:bottom_right[0], top_left[1]:bottom_right[1]]

    return cropped_image


def add_pad(image, new_height=700, new_width=700):
    height, width = image.shape
    final_image = np.ones((new_height, new_width))
    final_image = final_image * -1350

    pad_left = int((new_width - width) / 2)
    pad_top = int((new_height - height) / 2)

    final_image[pad_top:pad_top + height, pad_left:pad_left + width] = image

    return final_image


def resample(image, image_thickness, pixel_spacing):
    new_size = [1, 1, 1]

    x_pixel = float(pixel_spacing[0])
    y_pixel = float(pixel_spacing[1])

    size = np.array([x_pixel, y_pixel, float(image_thickness)])

    image_shape = np.array([image.shape[0], image.shape[1], 1])

    new_shape = image_shape * size
    new_shape = np.round(new_shape)
    resize_factor = new_shape / image_shape

    resampled_image = ndimage.interpolation.zoom(np.expand_dims(image, axis=2), resize_factor)

    return resampled_image



