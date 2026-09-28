"""
2015312911 김지환
Intelligent Agent 구축을 위한 손실함수, 규제기법 비교 프로그램

비교 항목 :
        손실함수 :
            - 평균제곱오차 (MSE)
            - 교차엔트로피
        규제기법 :
            - 데이터증대
            - 드롭아웃
            - 가중치감쇠

통계적 신뢰성을 위한 기법
    교차검증 [데이터를 분할하여 여러 번 반복]
    제거조사 [여러 선택 사항이 있을 때 선택 사항을 하나씩 빼고 측정]
"""

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

# 신경망에 들어갈 데이터 입력
(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train = x_train.reshape(60000, 28, 28, 1)
x_test = x_test.reshape(10000, 28, 28, 1)
x_train = x_train.astype(np.float32)/255.0
x_test = x_test.astype(np.float32)/255.0
y_train = tf.keras.utils.to_categorical(y_train, 10)
y_test = tf.keras.utils.to_categorical(y_test, 10)


# 신경망 모델 설계
# Convolution NN이용, 추가적으로 dropout과 l2 regularization 추가
# Batch normalization 기법 이용
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

# 하이퍼 매개변수 설정
batch_siz = 128
n_epoch = 8
k = 4

# 모델
tmp_model = build_model(dropout_rate=[0,0,0], l2_reg=0)
tmp_model.summary()


# 하이퍼 매개변수에 따라 교차 검증을 수행하고 정확률을 반환하는 함수
def cross_validation(loss_func, data_gen, dropout_rate, l2_reg):
    print("loss function used::", loss_func, "/ data generation::", data_gen, " ")
    print("dropout::", dropout_rate, " / l2 regularization::", l2_reg)

    accuracy = []
    loss = []
    for train_index, val_index in KFold(k).split(x_train):
        xtrain, xval = x_train[train_index], x_train[val_index]
        ytrain, yval = y_train[train_index], y_train[val_index]

        # 신경망 모델 설계
        cnn = build_model(dropout_rate, l2_reg)

        # 신경망을 학습하고 정확률 평가
        cnn.compile(loss=loss_func, optimizer=Adam(), metrics=['accuracy', loss_func])

        if data_gen:
            generator = ImageDataGenerator(rotation_range=3.0, width_shift_range=0.1, height_shift_range=0.1,
                                           horizontal_flip=True)
            cnn.fit_generator(generator.flow(x_train, y_train, batch_size=batch_siz), epochs=n_epoch,
                              validation_data=(x_test, y_test), verbose=2)
        else:
            cnn.fit(xtrain, ytrain, batch_size=batch_siz, epochs=n_epoch, validation_data=(x_test, y_test), verbose=2)
        accuracy.append(cnn.evaluate(xval, yval, verbose=0)[1])
        loss.append(cnn.evaluate(xval, yval, verbose=0)[2])
    return accuracy, loss


mse_acc_000, mse_loss_000 = cross_validation('mean_squared_error', False, [0.0, 0.0, 0.0], 0.0)
mse_acc_001, mse_loss_001 = cross_validation('mean_squared_error', False, [0.0, 0.0, 0.0], 0.01)
mse_acc_010, mse_loss_010 = cross_validation('mean_squared_error', False, [0.25, 0.25, 0.5], 0.0)
mse_acc_011, mse_loss_011 = cross_validation('mean_squared_error', False, [0.25, 0.25, 0.5], 0.01)
mse_acc_100, mse_loss_100 = cross_validation('mean_squared_error', True, [0.0, 0.0, 0.0], 0.0)
mse_acc_101, mse_loss_101 = cross_validation('mean_squared_error', True, [0.0, 0.0, 0.0], 0.01)
mse_acc_110, mse_loss_110 = cross_validation('mean_squared_error', True, [0.25, 0.25, 0.5], 0.0)
mse_acc_111, mse_loss_111 = cross_validation('mean_squared_error', True, [0.25, 0.25, 0.5], 0.01)

import matplotlib.pyplot as plt
plt.grid()
plt.title("Accuracy results from ablation study using cross validation and mean squared error as loss function")
plt.boxplot([mse_acc_000, mse_acc_001, mse_acc_010, mse_acc_011,
             mse_acc_100, mse_acc_101, mse_acc_110, mse_acc_111],
            labels=["000", "001", "010", "011",
                    "100", "101", "110", "111"])
plt.show()

plt.grid()
plt.title("Loss results from ablation study using cross validation and mean squared error as loss function")
plt.boxplot([mse_loss_000, mse_loss_001, mse_loss_010, mse_loss_011,
             mse_loss_100, mse_loss_101, mse_loss_110, mse_loss_111],
            labels=["000", "001", "010", "011",
                    "100", "101", "110", "111"])
plt.show()



ce_acc_000, ce_loss_000 = cross_validation('categorical_crossentropy', False, [0.0, 0.0, 0.0], 0.0)
ce_acc_001, ce_loss_001 = cross_validation('categorical_crossentropy', False, [0.0, 0.0, 0.0], 0.01)
ce_acc_010, ce_loss_010 = cross_validation('categorical_crossentropy', False, [0.25, 0.25, 0.5], 0.0)
ce_acc_011, ce_loss_011 = cross_validation('categorical_crossentropy', False, [0.25, 0.25, 0.5], 0.01)
ce_acc_100, ce_loss_100 = cross_validation('categorical_crossentropy', True, [0.0, 0.0, 0.0], 0.0)
ce_acc_101, ce_loss_101 = cross_validation('categorical_crossentropy', True, [0.0, 0.0, 0.0], 0.01)
ce_acc_110, ce_loss_110 = cross_validation('categorical_crossentropy', True, [0.25, 0.25, 0.5], 0.0)
ce_acc_111, ce_loss_111 = cross_validation('categorical_crossentropy', True, [0.25, 0.25, 0.5], 0.01)



plt.grid()
plt.title("Accuracy results from ablation study with cross validation and categorical-crossentropy as loss function")
plt.boxplot([ce_acc_000, ce_acc_001, ce_acc_010, ce_acc_011,
             ce_acc_100, ce_acc_101, ce_acc_110, ce_acc_111],
            labels=["000", "001", "010", "011",
                    "100", "101", "110", "111"])
plt.show()


plt.grid()
plt.title("Loss results from ablation study with cross validation and categorical-crossentropy as loss function")
plt.boxplot([ce_loss_000, ce_loss_001, ce_loss_010, ce_loss_011,
             ce_loss_100, ce_loss_101, ce_loss_110, ce_loss_111],
            labels=["000", "001", "010", "011",
                    "100", "101", "110", "111"])
plt.show()

for layer in tmp_model.layers:
    if 'conv' in layer.name:
        kernel, biases = layer.get_weights()
        print(layer.name, kernel.shape)

kernel, biases = tmp_model.layers[1].get_weights()
minv, maxv = kernel.min(), kernel.max()  # normalization of filter values
kernel = (kernel-minv)/(maxv-minv)
n_kernel = 64

plt.figure(figsize=(20,4))
plt.suptitle("kernels of conv2d")
for i in range(n_kernel):
    f = kernel[:,:,:,i]
    for j in range(1):
        plt.subplot(4, 16, j*n_kernel/3+i+1)
        plt.imshow(f[:,:,j], cmap='gray')
        plt.xticks([]); plt.yticks([])
        plt.title(str(i)+'_'+str(j))

plt.show()