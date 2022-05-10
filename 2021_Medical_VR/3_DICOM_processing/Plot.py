import numpy as np
import matplotlib.pyplot as plt
import pydicom
from Image_Preprocess import transform_to_hu, load_hu_image,\
    window_image, remove_noise, crop_image, add_pad, resample


def show_chest_image(file_path):

    medical_image = pydicom.read_file(file_path)
    image = medical_image.pixel_array
    hu_image = transform_to_hu(medical_image, image)
    brain_image = window_image(hu_image, 500, 200)
    plt.style.use('grayscale')
    plt.imshow(brain_image)
    plt.show()


def show_load_image(file_path, save=False):

    medical_image = pydicom.read_file(file_path)
    image = medical_image.pixel_array
    print(image.shape)
    # windowed image
    hu_image = transform_to_hu(medical_image, image)
    soft_tissue_image = window_image(hu_image, -600, 1500)
    bone_image = window_image(hu_image, 400, 1000)
    # image plotting
    plt.figure(figsize=(20, 10))
    plt.style.use('grayscale')
    plt.subplot(241)
    plt.imshow(image)
    plt.title('Original')
    plt.axis('off')
    plt.subplot(242)
    plt.imshow(hu_image)
    plt.title('Hu Image')
    plt.axis('off')
    plt.subplot(243)
    plt.imshow(soft_tissue_image)
    plt.title('Soft Tissue image')
    plt.axis('off')
    plt.subplot(244)
    plt.imshow(bone_image)
    plt.title('Bone image')
    plt.axis('off')
    plt.show()

def show_noise_removed_image(file_path):

    final_image = remove_noise(file_path)
    plt.style.use('grayscale')
    plt.imshow(final_image)
    plt.show()

def show_crop_image(file_path):
    final_image = remove_noise(file_path)
    cropped_image = crop_image(final_image)
    plt.style.use('grayscale')
    plt.imshow(cropped_image)
    plt.show()

def show_pad_image(file_path):
    final_image = remove_noise(file_path)
    final_image = crop_image(final_image)
    final_image = add_pad(final_image)

    plt.style.use('grayscale')
    plt.imshow(final_image)
    plt.show()

def show_improving_image(file_path):
    _ = remove_noise(file_path, True)


def show_resample(filepath1, filepath2):
    first_medical_image = pydicom.read_file(filepath1)
    second_medical_image = pydicom.read_file(filepath2)
    first_image =(first_medical_image.pixel_array)
    print(first_image.shape)

    image_thickness = np.abs(first_medical_image.ImagePositionPatient[2]
                             - second_medical_image.ImagePositionPatient[2])
    pixel_spacing = first_medical_image.PixelSpacing

    resampled_image = resample(first_image, image_thickness, pixel_spacing)
    print(np.squeeze(resampled_image).shape)


# final_image = remove_noise("1-169.dcm")
# plt.imshow(final_image)
# plt.show()
# final_image = crop_image(final_image)
# plt.imshow(final_image)
# plt.show()
# final_image = add_pad(final_image)
# plt.imshow(final_image)
# plt.show()
