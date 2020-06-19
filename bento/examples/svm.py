import numpy as np
import pandas as pd

from sklearn import datasets, model_selection, preprocessing, svm


def load(n_samples=100, dataset="moons", noise=0.5, kernel="rbf"):
    # Generate the base data with sklearn.datasets
    if dataset == "moons":
        coords, labels = datasets.make_moons(
            n_samples=n_samples, noise=noise, random_state=0
        )

    elif dataset == "circles":
        coords, labels = datasets.make_circles(
            n_samples=n_samples, noise=noise, factor=0.5, random_state=1
        )

    # preprocessing.StandardScaler
    X_train, X_test, y_train, y_test = model_selection.train_test_split(
        X, y, test_size=0.4
    )

    # Train SVM
    clf = svm.SVC(kernel=kernel, probability=True)
    clf.fit(X_train, y_train)

    axis_ticks = np.arange(-3, 3, 1)
    mesh = np.meshgrid(axis_ticks, axis_ticks)
    df = pd.DataFrame({"x": mesh[0].ravel(), "y": mesh[1].ravel(),})

    df = pd.DataFrame()
    df["x"] = [pair[0] for pair in coords]
    df["y"] = [pair[1] for pair in coords]
    df["label"] = labels
    data = {
        "df": df,
        "types": {"x": float, "y": float, "label": bool},
        "columns": ["x", "y", "label"],
    }
    return data
