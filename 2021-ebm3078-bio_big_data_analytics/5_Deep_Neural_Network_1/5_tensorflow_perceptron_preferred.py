import tensorflow as tf


x = [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]]
y = [[-1], [1], [1], [1]]

# 가중치 초기화
w = tf.Variable(tf.random.uniform([2, 1], -0.5, 0.5))
b = tf.Variable(tf.zeros([1]))

# 옵티마이저
opt = tf.keras.optimizers.SGD(learning_rate=0.1)


# 전방 계산
def forward():
    s = tf.add(tf.matmul(x, w), b)
    o = tf.tanh(s)
    return o


# 손실 함수 정의
def loss():
    o = forward()
    return tf.reduce_mean((y-o)**2)


# 500 세대까지 학습(100세대마다 학습 정보 출력)
for i in range(500):
    opt.minimize(loss, var_list=[w,b])
    if i % 100 == 0:
        print('loss at epoch', i, '=', loss().numpy())

# 학습된 퍼셉트론으로 OR 데이터 예측
o = forward()
print(o)



