from abc import ABC, abstractmethod
import pandas as pd
from typing import Any
from io import BytesIO

class IPlotStrategy(ABC):
    @abstractmethod
    def plot(self, df: pd.DataFrame, **kwargs: Any) -> bytes:
        """
        Genera un gráfico a partir de df y kwargs,
        y devuelve los bytes de la imagen en formato PNG.
        """
        ...

class ChartStrategy(IPlotStrategy):
    pass
