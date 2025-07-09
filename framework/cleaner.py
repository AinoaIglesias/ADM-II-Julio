from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Optional, Union, Dict, Any


class ICleaner(ABC):
    @abstractmethod
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Recibe un DataFrame crudo y devuelve otro limpio con un log de limpieza en df.attrs["cleaning_log"].
        """
        ...

class Cleaner(ICleaner):
    def __init__(
        self,
        date_cols: Optional[List[str]] = None,
        date_patterns: List[str] = ("date", "fecha", "Start_Time"),
        strategy_numeric: str = "mean",       # "mean", "zero", "drop" o "none"
        strategy_categorical: str = "fill",   # "fill", "drop" o "none"
        drop_empty_const: bool = True,
        null_threshold: float = 0.7,
    ):
        """
        date_cols: lista de columnas a convertir a datetime;
                   si es None, busca columnas cuyo nombre contenga cualquiera de date_patterns.
        strategy_numeric: cómo tratar nulos en numéricas.
        strategy_categorical: cómo tratar nulos en categóricas.
        drop_empty_const: eliminar columnas vacías o de valor único.
        null_threshold: umbral para eliminar columnas con > este ratio de nulos.
        """
        self.date_cols = date_cols
        self.date_patterns = date_patterns
        self.strategy_numeric = strategy_numeric
        self.strategy_categorical = strategy_categorical
        self.drop_empty_const = drop_empty_const
        self.null_threshold = null_threshold

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        log: List[str] = []

        # 1) columnas de fecha
        if self.date_cols is None:
            date_cols = [
                c for c in df.columns
                if any(pat in c.lower() for pat in self.date_patterns)
            ]
        else:
            date_cols = [c for c in self.date_cols if c in df.columns]

        for c in date_cols:
            try:
                df[c] = pd.to_datetime(df[c])
                log.append(f"Columna '{c}' convertida a datetime.")
            except Exception:
                log.append(f"Columna '{c}' NO se pudo convertir a datetime.")

        # 3) eliminar columnas vacías o constantes
        if self.drop_empty_const:
            before = df.shape[1]
            df = df.dropna(axis=1, how="all")
            df = df.loc[:, df.nunique() > 1]
            removed = before - df.shape[1]
            if removed:
                log.append(f"Eliminadas {removed} columnas vacías o constantes.")

        # 4) nulos
        for c in list(df.columns):
            pct = df[c].isnull().mean()
            if pct > self.null_threshold:
                df.drop(columns=[c], inplace=True)
                log.append(f"Columna '{c}' eliminada (> {pct:.0%} nulos).")
                continue

            # 4a) columnas numéricas
            if pd.api.types.is_numeric_dtype(df[c]):
                null_count = df[c].isnull().sum()
                strat = self.strategy_numeric
                if strat == "mean" and null_count > 0:
                    df[c] = df[c].fillna(df[c].mean())
                    log.append(f"'{c}' imputada con media.")
                elif strat == "zero":
                    df[c] = df[c].fillna(0)
                    log.append(f"'{c}' imputada con cero.")
                elif strat == "drop" and null_count > 0:
                    before_rows = len(df)
                    df = df.dropna(subset=[c])
                    dropped = before_rows - len(df)
                    log.append(f"Dropped {dropped} filas con nulos en '{c}'.")

            # 4b) columnas categóricas
            else:
                null_count = df[c].isnull().sum()
                strat = self.strategy_categorical
                if strat == "fill" and null_count > 0:
                    # si ya es Categorical, añadimos el nuevo nivel
                    if pd.api.types.is_categorical_dtype(df[c]):
                        df[c] = df[c].cat.add_categories("Desconocido")
                    df[c] = df[c].fillna("Desconocido")
                    log.append(f"'{c}' imputada con 'Desconocido'.")
                elif strat == "drop" and null_count > 0:
                    before_rows = len(df)
                    df = df.dropna(subset=[c])
                    dropped = before_rows - len(df)
                    log.append(f"Dropped {dropped} filas con nulos en '{c}'.")

        # 5) mensajes si quedan nulos
        remaining = int(df.isnull().sum().sum())
        if remaining:
            log.append(f"⚠️ Quedan {remaining} valores nulos tras limpieza.")

        df.attrs["cleaning_log"] = log
        return df



class TypeOnlyCleaner(ICleaner):
    """
    Solo convierte el tipo de las columnas indicadas.
    """
    def __init__(self, dtype_map: Dict[str, Any]):
        """
        dtype_map: mapa columna → dtype (ej. {'station': 'category', 'CO':'float32'})
        """
        self.dtype_map = dtype_map

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        log: List[str] = []

        for col, dtype in self.dtype_map.items():
            if col not in df.columns:
                log.append(f"⚠️ Columna '{col}' no existe, no se puede convertir a {dtype}.")
                continue
            try:
                df[col] = df[col].astype(dtype)
                log.append(f"Columna '{col}' convertida a tipo {dtype}.")
            except Exception as e:
                log.append(f"❌ No se pudo convertir '{col}' a {dtype}: {e!s}")

        df.attrs["cleaning_log"] = log
        return df