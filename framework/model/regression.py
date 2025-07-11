from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from .modelbase import IModelStrategy
import pandas as pd

class LinearRegressionModel(IModelStrategy):
    def __init__(self, **kw):
        self.reg = LinearRegression(**kw)

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.reg.fit(X, y)
        return self

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return pd.Series(self.reg.predict(X), index=X.index)

    def evaluate(self, X: pd.DataFrame, y: pd.Series):
        y_pred = self.predict(X)
        return {
            "mse": mean_squared_error(y, y_pred),
            "r2": r2_score(y, y_pred)
        }
