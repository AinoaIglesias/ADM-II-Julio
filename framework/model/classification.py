from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
from .modelbase import IModelStrategy
import pandas as pd

class LogisticClassification(IModelStrategy):
    def __init__(self, **kw):
        self.clf = LogisticRegression(**kw)

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.clf.fit(X, y)
        return self

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return pd.Series(self.clf.predict(X), index=X.index)

    def evaluate(self, X: pd.DataFrame, y: pd.Series):
        y_pred = self.predict(X)
        return {
            "accuracy": accuracy_score(y, y_pred),
            "confusion_matrix": confusion_matrix(y, y_pred).tolist()
        }
