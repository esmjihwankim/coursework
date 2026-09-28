import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.manifold import TSNE
import pandas as pd

digits = load_digits()
features = digits['data']
feature_names = digits['feature_names']

digits_df = pd.DataFrame(features, columns=feature_names)
print(digits_df)

_, axes = plt.subplots(nrows=1, ncols=4, figsize=(10, 3))
for ax, image, label in zip(axes, digits.images, digits.target):
    ax.set_axis_off()
    ax.imshow(image, cmap=plt.cm.gray_r, interpolation="nearest")
    ax.set_title("Training: %i" %label)
plt.show()

X = digits.data[:500]
y = digits.target[:500]
tsne = TSNE(n_components=2, random_state=0)
X_2d = tsne.fit_transform(X)
digits_ids = range(len(digits.target_names))
plt.figure(figsize=(6,5))
colors = 'aqua', 'azure', 'coral', 'gold', 'green', 'fuchsia', 'maroon', 'purple', 'red', 'orange'
for i, c, label in zip(digits_ids, colors, digits.target_names):
    plt.scatter(X_2d[y == i, 0], X_2d[y == i, 1], c=c, label=label)
plt.legend()
plt.show()
