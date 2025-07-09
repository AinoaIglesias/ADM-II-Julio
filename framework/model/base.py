from abc import ABC, abstractmethod
import pandas as pd
from typing import Any, Dict

class IModelStrategy(ABC):
    @abstractmethod
    def fit(self, X: pd.DataFrame, y: pd.Series) -> Any:
        """
        Ajusta el modelo con X (features) y y (target).
        Devuelve self o el objeto entrenado.
        """
        ...

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> pd.Series:
        """
        Predice sobre nuevas features X.
        """
        ...

    @abstractmethod
    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """
        Devuelve un dict con métricas (p.ej. accuracy, MSE, R2, silhouette…).
        """
        ...
