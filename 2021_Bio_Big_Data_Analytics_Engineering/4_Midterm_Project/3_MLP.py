from sklearn import datasets
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
import numpy as np


"""
2015312911 김지환 
Multi Layer Perceptron
"""

# 데이터셋을 읽고 훈련 집합과 테스트 집합으로 분할
digit = datasets.load_digits()
x_train, x_test, y_train, y_test = train_test_split(digit.data, digit.target, train_size=0.6)

# fit 함수로 Perceptron 학습
mlp = MLPClassifier(hidden_layer_sizes=(100), learning_rate_init=0.001, batch_size=32, max_iter=300, solver='sgd', verbose=True)
mlp.fit(x_train, y_train)  # digit 데이터로 모델링
res = mlp.predict(x_test)  # 테스트 집합으로 예측

# 혼동 행렬
conf = np.zeros((10, 10))
for i in range(len(res)):
    conf[res[i]][y_test[i]] += 1
print(conf)
print(len(conf[0]))



############################
# Performance Metrics
############################


# 정확률 (Accuracy)
no_correct = 0
for i in range(10):
    no_correct += conf[i][i]
accuracy = no_correct / len(res)
print("테스트 집합에 대한 정확률은 ", accuracy * 100, "% 입니다.")
print("표준 라이브러리로 확인한 정확률 ", accuracy_score(y_test, res))


# 정밀도 (Precision)
tp_precision = 0
fp_precision = 0
precision = 0
for i in range(10):
    tp_precision = conf[i][i]
    for j in range(10):
        if j == i:
            continue
        fp_precision += conf[i][j]
    precision += tp_precision / (tp_precision + fp_precision)
    fp_precision = 0
    tp_precision = 0
precision /= len(conf[0])
print("테스트 집합에 대한 정밀도는 ", precision * 100, "% 입니다.")
print("표준 라이브러리로 확인한 정밀도는 ", precision_score(y_test, res, average='macro'))

# 재현률(Recall)
tp_recall = 0
fn_recall = 0
recall = 0
for i in range(10):
    tp_recall = conf[i][i]
    for j in range(10):
        if j == i:
            continue
        fn_recall += conf[j][i]
    recall += tp_recall / (tp_recall + fn_recall)
    tp_recall = 0
    fn_recall = 0
recall /= len(conf[0])
print("테스트 집합에 대한 재현률 ", recall * 100, "% 입니다.")
print("표준 라이브러리로 확인한 재현률은 ", recall_score(y_test, res, average='macro'))
