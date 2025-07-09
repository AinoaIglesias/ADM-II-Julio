# framework/processor/base.py

from abc import ABC, abstractmethod
import pandas as pd
from typing import Any, Dict, List, Tuple
import io

class IProcessor(ABC):
    @abstractmethod
    def get_shape(self, df: pd.DataFrame) -> Tuple[int,int]:
        ...

    @abstractmethod
    def get_dtypes(self, df: pd.DataFrame) -> Dict[str,str]:
        ...

    @abstractmethod
    def get_columns(self, df: pd.DataFrame) -> List[str]:
        ...

    @abstractmethod
    def get_info(self, df: pd.DataFrame) -> str:
        ...

    @abstractmethod
    def get_null_percentages(self, df: pd.DataFrame) -> Dict[str,float]:
        ...

    @abstractmethod
    def get_unique_counts(self, df: pd.DataFrame) -> Dict[str,int]:
        ...

    @abstractmethod
    def get_unique_values(self, df: pd.DataFrame, n: int = 10) -> Dict[str, List[Any]]:
        ...

    @abstractmethod
    def get_descriptive_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        ...


class DataProcessor(IProcessor):
    def get_shape(self, df: pd.DataFrame) -> Tuple[int,int]:
        return df.shape

    def get_dtypes(self, df: pd.DataFrame) -> Dict[str,str]:
        return {c: str(dt) for c, dt in df.dtypes.items()}

    def get_columns(self, df: pd.DataFrame) -> List[str]:
        return df.columns.tolist()

    def get_info(self, df: pd.DataFrame) -> str:
        # captura el output de df.info() en un string
        buf = io.StringIO()
        df.info(buf=buf)
        return buf.getvalue()

    def get_null_percentages(self, df: pd.DataFrame) -> Dict[str,float]:
        # porcentaje de nulos por columna, redondeado
        pct = (df.isnull().mean() * 100).round(2)
        return pct.to_dict()

    def get_unique_counts(self, df: pd.DataFrame) -> Dict[str,int]:
        # número de valores únicos por columna
        return df.nunique().to_dict()

    def get_unique_values(self, df: pd.DataFrame, n: int = 10) -> Dict[str, List[Any]]:
        # primeros n valores únicos de cada columna
        uniq = {}
        for c in df.columns:
            vals = pd.Series(df[c].dropna().unique())
            uniq[c] = vals.head(n).tolist()
        return uniq

    def get_descriptive_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.describe()
