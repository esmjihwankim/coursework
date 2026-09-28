
"""
numpy 내부구조, 동작원리
1D : vector
2D : Matrix
nD : Tensor
"""

import numpy as np
np.random.seed(42)

x = np.random.randint(low=0, high=10, size=(4,3))
print(f"x = {x}")
print(f"x shape: {x.shape}")
print(f"x strides: {x.strides}")
print(x.__array_interface__['data'])

"""
actual data in 1D array. 
Has attributes such as its location in 
memory space, shape, stride info

Even after reshape, other data 
points to the original data
"""

x1 = x.reshape((2, 6))
print(x.__array_interface__['data'])
print(x1.__array_interface__['data'])

"""
to prevent unintended tranformation of data,
copy then reshape
"""
x1 = x.reshape((2,6)).copy()
