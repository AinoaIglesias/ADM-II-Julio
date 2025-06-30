from abc import ABC, abstractmethod

class ChartStrategy(ABC):
    @abstractmethod
    def plot(self, df, x_col, y_col, buffer, agregacion, grupo=None):
        pass
