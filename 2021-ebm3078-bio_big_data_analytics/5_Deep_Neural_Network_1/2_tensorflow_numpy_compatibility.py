import tensorflow as tf
import numpy as np

t = tf.random.uniform([2, 3], 0, 1)
n = np.random.uniform(0, 1, [2, 3])
print("tensorflow로 생성한 텐서:\n", t)
print("numpy로 생성한 ndarray:\n", n)

res = t+n
print("덧셈결과:\n", res)

