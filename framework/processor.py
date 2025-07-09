from abc import ABC, abstractmethod
import pandas as pd
from typing import Tuple, Dict, List

class IProcessor(ABC):
    @abstractmethod
    def get_shape(self, df: pd.DataFrame) -> Tuple[int,int]:
        pass

    @abstractmethod
    def get_dtypes(self, df: pd.DataFrame) -> Dict[str,str]:
        pass

    @abstractmethod
    def get_columns(self, df: pd.DataFrame) -> List[str]:
        pass

class DataProcessor(IProcessor):
    def get_shape(self, df: pd.DataFrame) -> Tuple[int,int]:
        return df.shape

    def get_dtypes(self, df: pd.DataFrame) -> Dict[str,str]:
        return {c: str(dt) for c,dt in df.dtypes.items()}

    def get_columns(self, df: pd.DataFrame) -> List[str]:
        return df.columns.tolist()
