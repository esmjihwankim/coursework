import numpy as np
import pandas as pd
import seaborn as sb
import matplotlib as plt
import math
import torch

# 데이터 준비 / 위치 확인
x1 = pd.read_csv('K:/Dev/ML+DL/Data_0905', header=None)
x2 = pd.read_csv('K:/Dev/ML+DL/Data_0905', header=None)
x3 = pd.read_csv('K:/Dev/ML+DL/Data_0905', header=None)
x4 = pd.read_csv('K:/Dev/ML+DL/Data_0905', header=None)
x5 = pd.read_csv('K:/Dev/ML+DL/Data_0905', header=None)


# Trainset
X1 = pd.concat([x2, x3, x4, x5])
X2 = pd.concat([x1, x3, x4, x5])
X3 = pd.concat([x1, x2, x4, x5])
X4 = pd.concat([x1, x2, x3, x5])
X5 = pd.concat([x1, x2, x3, x4])
Y1 = X1.pop(0)
Y2 = X2.pop(0)
Y3 = X3.pop(0)
Y4 = X4.pop(0)
Y5 = X5.pop(0)

# Validation Set
y1 = x1.pop(0)
y2 = x2.pop(0)
y3 = x3.pop(0)
y4 = x4.pop(0)
y5 = x5.pop(0)

# Convert to Tensor
X1_tensor = torch.tensor(X1.values, dtype=torch.float32)
Y1_tensor = torch.tensor(Y1.values, dtype=torch.float32)
x1_tensor = torch.tensor(x1.values, dtype=torch.float32)
y1_tensor = torch.tensor(y1.values, dtype=torch.float32)

# Layer 쌓기 : Linear (input의 수, output의 수)
# 경우에 따라 Dropout 추가
# Layer의 수는 시행착오를 거쳐 실험적으로 조정
model = torch.nn.Sequential(
    torch.nn.Linear(42, 85),
    torch.nn.LeakyReLU(),       # 활성화 함수 : ReLU, LeakyReLU, tanh등을 사용
    torch.nn.Linear(85, 85),
    torch.nn.LeakyReLU(),
    torch.nn.Linear(85, 1),     # 마지막 레이어(N', 1) -> Linear
    torch.nn.Sigmoid(dim=1),    # 0 에서 1 사이로 바꾸어줌. 1이면 high, 0이면 low
    torch.nn.Flatten(0, 1)
)

epoch = 2000
learning_rate = 1e-4
loss_fn = torch.nn.BCELoss()
optimizer = torch.optim.Adam(model.parameters(), lr = learning_rate)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer='min')

for t in range(epoch):
    optimizer.zero_grad()
    y_pred = model(x1_tensor)
    loss = loss_fn(y_pred, Y1_tensor)
    val_y_pred = model(x1_tensor)
    val_loss = loss_fn(val_y_pred, y1_tensor)
    if t % 100 == 99:
        print(t+1, 'train rmse: ', loss.item(), ' validation rmse:  ', val_loss.item())

    loss.backward()
    optimizer.step()
    scheduler.step(val_loss)



