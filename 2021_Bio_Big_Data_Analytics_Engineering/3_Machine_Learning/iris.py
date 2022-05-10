from sklearn.datasets import load_iris
from sklearn import svm
import pandas as pd
import matplotlib.pyplot as plt
import mglearn
import plotly.express as px

d = load_iris()
print(d.DESCR)  # data set 특징 설명

print(d.target)
print(d['target'].shape)

s = svm.SVC(gamma=0.1, C=10)
s.fit(d.data, d.target)

new_d = [[6.4,3.2,6.0,2.5], [7.1,3.1,4.7,1.35]]

res = s.predict(new_d)
print("새로운 2개 샘플의 부류는", res)

iris_dataframe = pd.DataFrame(d.data, columns=d.feature_names)
scatter_plot = pd.plotting.scatter_matrix(iris_dataframe, c=d.target, figsize=(15, 15), marker='o', hist_kwds={'bins':20}, s=60, alpha=0.8, cmap=mglearn.cm3)
plt.show()


df = px.data.iris()
fig = px.scatter_3d(df, x='sepal_length', y='sepal_width', z='petal_width', color='species')
fig.show(renderer="browser")

