from abc import ABC, abstractmethod
import pandas as pd

class BasePlotter(ABC):
    @abstractmethod
    def plot(self, df: pd.DataFrame, x: str, y: str, group_col: str = None):
        pass
