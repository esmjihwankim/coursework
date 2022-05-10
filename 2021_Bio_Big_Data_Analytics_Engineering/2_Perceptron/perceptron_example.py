
import numpy as np

""" First Example """
x2 = np.array([1,0,1])
w = np.array([-0.5, 1.0, 1.0])
s = sum(x2 * w)

if s >= 0:
    o = 1
else:
    o = -1

print(s)
print(o)


""" Second Example """
x = np.array([[1,0,0], [1,0,1], [1,1,0], [1,1,1]])

w = np.array([-0.5, 1.0, 1.0])
s = np.sum(x*w, axis=1)

o = np.where(s >= 0, 1, -1)

print(s)
print(o)


