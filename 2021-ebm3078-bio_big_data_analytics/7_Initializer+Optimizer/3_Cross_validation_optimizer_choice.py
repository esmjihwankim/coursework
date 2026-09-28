
import numpy as np
import tensorflow as tf
from tensorflow.keras.datasets import fashion_mnist
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import SGD,Adam,Adagrad,RMSprop
from sklearn.model_selection import KFold

# Fashion MNIST를 읽고 신경망에 입력할 형태로 변환
(x_train, y_train), (x_test, y_test) = fashion_mnist.load_data()

x_train = x_train.reshape(60000, 28*28)
x_test = x_test.reshape(10000, 28*28)
x_train = x_train.astype(np.float32)/255.0
x_test = x_test.astype(np.float32)/255.0
y_train = tf.keras.utils.to_categorical(y_train, num_classes=10)
y_test = tf.keras.utils.to_categorical(y_test, num_classes=10)

# Neural Network Structure
n_input = 28*28
n_hidden1 = 1024
n_hidden2 = 512
n_hidden3 = 512
n_hidden4 = 512
n_output = 10

# Hyperparameters
batch_siz = 256
n_epoch = 20
k = 5


# model - building function
def build_model():
    model = Sequential()
    model.add(Dense(units=n_hidden1, activation='relu', input_shape=(n_input, )))
    model.add(Dense(units=n_hidden2, activation='relu'))
    model.add(Dense(units=n_hidden3, activation='relu'))
    model.add(Dense(units=n_hidden4, activation='relu'))
    model.add(Dense(units=n_output, activation='softmax'))
    return model


def cross_validation(opt):
    accuracy = []
    for train_index, val_index in KFold(k).split(x_train):
        xtrain, xval = x_train[train_index], x_train[val_index]
        ytrain, yval = y_train[train_index], y_train[val_index]
        dmlp = build_model()
        dmlp.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])
        dmlp.fit(xtrain, ytrain, batch_size=batch_siz, epochs=n_epoch, verbose=0)
        accuracy.append(dmlp.evaluate(xval, yval, verbose=0)[1])
    return accuracy


# cross validation for 4 optimizers
acc_sgd = cross_validation(SGD())
acc_adam = cross_validation(Adam())
acc_adagrad= cross_validation(Adagrad())
acc_rmsprop = cross_validation(RMSprop())

# compare accuracy of the 4 optimizers
print("SGD:", np.array(acc_sgd).mean())
print("Adam:", np.array(acc_adam).mean())
print("Adagrad:", np.array(acc_adagrad).mean())
print("RMSprop:", np.array(acc_rmsprop).mean())


import matplotlib.pyplot as plt
# 네 옵티마이저의 정확률을 박스플롯으로 비교
plt.boxplot([acc_sgd, acc_adam, acc_adagrad, acc_rmsprop], labels=["SGD", "Adam", "Adagrad", "RMSProp"])
plt.grid()
plt.show()