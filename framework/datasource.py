from abc import ABC, abstractmethod
import pandas as pd

class IDataSource(ABC):
    @abstractmethod
    def load(self) -> pd.DataFrame:
        """Carga y devuelve un DataFrame."""
        pass

class CSVDataSource(IDataSource):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> pd.DataFrame:
        return pd.read_csv(self.file_path)

class JSONDataSource(IDataSource):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> pd.DataFrame:
        return pd.read_json(self.file_path)
