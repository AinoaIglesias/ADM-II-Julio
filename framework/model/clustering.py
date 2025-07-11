from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from .modelbase import IModelStrategy
import pandas as pd

class KMeansClustering(IModelStrategy):
    def __init__(self, n_clusters=3, **kw):
        self.n_clusters = n_clusters
        self.km = KMeans(n_clusters=n_clusters, **kw)

    def fit(self, X: pd.DataFrame, y=None):
        # encuentra los centros de los n_clusters
        self.km.fit(X)
        return self

    def predict(self, X: pd.DataFrame) -> pd.Series:
        #asigna a cada fila de X un número de clúster
        return pd.Series(self.km.predict(X), index=X.index)

    def evaluate(self, X: pd.DataFrame, y=None):  #devuelve inercia y puntuación de silhouette.
        labels = self.predict(X)
        return {
            "inertia": float(self.km.inertia_),
            "silhouette": silhouette_score(X, labels)
        }
