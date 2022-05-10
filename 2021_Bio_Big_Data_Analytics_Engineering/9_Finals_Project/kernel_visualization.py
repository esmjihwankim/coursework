import numpy as np
import tensorflow as tf
from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import KFold

from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import regularizers

def build_model(dropout_rate, l2_reg):
    model = Sequential()

    model.add(Conv2D(filters=64, kernel_size=(3, 3), activation="relu", input_shape=(28, 28, 1)))
    model.add(Conv2D(filters=64, kernel_size=(3, 3), activation="relu"))

    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(BatchNormalization())
    model.add(Conv2D(filters=128, kernel_size=(3, 3), activation="relu"))
    # model.add(Conv2D(filters=128, kernel_size = (3,3), activation="relu")) 레이어 하나 삭제
    model.add(Dropout(dropout_rate[0]))

    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(BatchNormalization())
    model.add(Conv2D(filters=256, kernel_size=(3, 3), activation="relu"))
    model.add(Dropout(dropout_rate[1]))

    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Flatten())
    model.add(BatchNormalization())
    model.add(Dense(512, activation="relu"))
    model.add(Dropout(dropout_rate[2]))

    model.add(Dense(10, activation="softmax", kernel_regularizer=regularizers.l2(l2_reg)))

    return model

cnn = build_model([0,0,0], 0)
# 커널 시각화
import matplotlib.pyplot as plt
for layer in cnn.layers:
    if 'conv' in layer.name:
        kernel, biases = layer.get_weights()
        print(layer.name, kernel.shape)

kernel, biases = cnn.layers[1].get_weights()
minv, maxv = kernel.min(), kernel.max()  # normalization of filter values
kernel = (kernel-minv)/(maxv-minv)
n_kernel = 64

plt.figure(figsize=(20,4))
plt.suptitle("kernels of conv2d-first layer:(3, 3, 1, 64)")
for i in range(n_kernel):
    f = kernel[:,:,:,i]
    for j in range(1):
        plt.subplot(4, 16, j*n_kernel/3+i+1)
        plt.imshow(f[:,:,j], cmap='gray')
        plt.xticks([]); plt.yticks([])
        plt.title(str(i)+'_'+str(j))

plt.show()
