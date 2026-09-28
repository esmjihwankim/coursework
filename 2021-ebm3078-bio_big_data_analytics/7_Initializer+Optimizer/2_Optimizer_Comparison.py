import numpy as np
import tensorflow as tf
from tensorflow.keras.datasets import fashion_mnist
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import SGD,Adam,Adagrad,RMSprop

# fashion MNIST 읽어 와서 신경망에 입력할 형태로 변환
(x_train, y_train), (x_test, y_test) = fashion_mnist.load_data()
x_train = x_train.reshape(60000, 784)
x_test = x_test.reshape(10000, 784)
x_train = x_train.astype(np.float32)/255.0
x_test = x_test.astype(np.float32)/255.0
y_train = tf.keras.utils.to_categorical(y_train, 10)
y_test = tf.keras.utils.to_categorical(y_test, 10)

# 신경망 구조 설정
n_input = 784
n_hidden1 = 1024
n_hidden2 = 512
n_hidden3 = 512
n_hidden4 = 512
n_output = 10

# 하이퍼 매개변수 설정
batch_size = 128
n_epoch = 30

# 모델을 설계해주는 함수 (모델을 나타내는 객체 model을 반환)
def build_model():
    model = Sequential()
    model.add(Dense(units=n_hidden1, activation='relu', input_shape=(n_input,)))
    model.add(Dense(units=n_hidden2, activation='relu'))
    model.add(Dense(units=n_hidden3, activation='relu'))
    model.add(Dense(units=n_hidden4, activation='relu'))
    model.add(Dense(units=n_output, activation='softmax'))
    return model

# SGD Optimizer 사용하는 모델
dmlp_sgd = build_model()
dmlp_sgd.compile(loss='categorical_crossentropy', optimizer=SGD(), metrics=['accuracy'])
hist_sgd = dmlp_sgd.fit(x_train, y_train, batch_size=batch_size, epochs=n_epoch,
                      validation_data=(x_test, y_test), verbose=2)

# Adam Optimizer 사용하는 모델
dmlp_adam = build_model()
dmlp_adam.compile(loss='categorical_crossentropy', optimizer=Adam(), metrics=['accuracy'])
hist_adam = dmlp_adam.fit(x_train, y_train, batch_size=batch_size, epochs=n_epoch,
                        validation_data=(x_test, y_test), verbose=2)

# Adagrad Optimizer 사용하는 모델
dmlp_adagrad = build_model()
dmlp_adagrad.compile(loss='categorical_crossentropy', optimizer=Adagrad(), metrics=['accuracy'])
hist_adagrad = dmlp_adagrad.fit(x_train, y_train, batch_size=batch_size, epochs=n_epoch,
                        validation_data=(x_test, y_test), verbose=2)

# RMSProp Optimizer 사용하는 모델
dmlp_rmsprop = build_model()
dmlp_rmsprop.compile(loss='categorical_crossentropy', optimizer=RMSprop(), metrics=['accuracy'])
hist_rmsprop = dmlp_rmsprop.fit(x_train, y_train, batch_size=batch_size, epochs=n_epoch,
                        validation_data=(x_test, y_test), verbose=2)


# 네 모델의 정확률을 출력
print('SGD 정확률은', dmlp_sgd.evaluate(x_test, y_test, verbose=0)[1]*100)
print('Adam 정확률은', dmlp_adam.evaluate(x_test, y_test, verbose=0)[1]*100)
print('Adagrad 정확률은', dmlp_adagrad.evaluate(x_test, y_test, verbose=0)[1]*100)
print('RMSProp 정확률은', dmlp_rmsprop.evaluate(x_test, y_test, verbose=0)[1]*100)

import matplotlib.pyplot as plt
# 네 모델의 정확률을 하나의 그래프에서 비교
plt.plot(hist_sgd.history['accuracy'], 'r')
plt.plot(hist_sgd.history['val_accuracy'], 'r--')
plt.plot(hist_adam.history['accuracy'], 'g')
plt.plot(hist_adam.history['val_accuracy'], 'g--')
plt.plot(hist_adagrad.history['accuracy'], 'b')
plt.plot(hist_adagrad.history['val_accuracy'], 'b--')
plt.plot(hist_rmsprop.history['accuracy'], 'm')
plt.plot(hist_rmsprop.history['val_accuracy'], 'm--')
plt.title('Model accuracy comparison between optimizers')
plt.ylim((0.6, 1.0))
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train_sgd', 'Val_sgd', 'Train_adam', 'Val_adam', 'Train_adagrad',
            'Val_adagrad', 'Train_rmsprop', 'Val_rmsprop'], loc='best')
plt.grid()
plt.show()