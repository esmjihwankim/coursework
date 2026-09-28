import tensorflow as tf
import tensorflow.keras.datasets as ds
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# MNIST 읽고 텐서 모양 출력
(x_train, y_train), (x_test, y_test) = ds.mnist.load_data()
yy_train = tf.one_hot(y_train, 10, dtype=tf.int8)
print("MNIST:", x_train.shape, y_train.shape, yy_train.shape)

# CIFAR-10 읽고 텐서 모양 출력
(x_train, y_train), (x_test, y_test) = ds.cifar10.load_data()
yy_train = tf.one_hot(y_train, 10, dtype = tf.int8)
print("CIFAR-10:", x_train.shape, y_train.shape, yy_train.shape)

# Boston Housing 읽고 텐서 모양 출력
(x_train, y_train), (x_test, y_test) = ds.boston_housing.load_data()
print("Boston Housing:", x_train.shape, y_train.shape)

# Reuters 읽고 텐서 모양 출력
(x_train, y_train), (x_test, y_test) = ds.reuters.load_data()
print("Reuters:", x_train.shape, y_train.shape)
