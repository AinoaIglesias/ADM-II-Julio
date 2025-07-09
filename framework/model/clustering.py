from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from .base import IModelStrategy
import pandas as pd

class KMeansClustering(IModelStrategy):
    def __init__(self, n_clusters=3, **kw):
        self.n_clusters = n_clusters
        self.km = KMeans(n_clusters=n_clusters, **kw)

    def fit(self, X: pd.DataFrame, y=None):
        self.km.fit(X)
        return self

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return pd.Series(self.km.predict(X), index=X.index)

    def evaluate(self, X: pd.DataFrame, y=None):
        labels = self.predict(X)
        return {
            "inertia": float(self.km.inertia_),
            "silhouette": silhouette_score(X, labels)
        }
