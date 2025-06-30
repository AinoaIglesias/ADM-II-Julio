import pandas as pd

def clean_dataset(df, strategy_numeric="mean", strategy_categorical="fill", drop_cols=True, null_threshold=0.7):
    """
    Limpia el dataset:
    - Convierte fechas
    - Elimina o imputa columnas según porcentaje de nulos
    - Elimina columnas vacías o constantes
    """

    df = df.copy()
    cleaning_log = []

    # 1. Convertir columnas que parecen fechas
    for col in df.columns:
        if "date" in col.lower() or "fecha" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col])
                cleaning_log.append(f"Columna '{col}' convertida a datetime.")
            except Exception:
                cleaning_log.append(f"Columna '{col}' NO se pudo convertir a datetime.")

    # 2. Eliminar columnas vacías o constantes
    if drop_cols:
        before = df.shape[1]
        df = df.dropna(axis=1, how='all')  # columnas completamente vacías
        df = df.loc[:, df.nunique() > 1]   # columnas constantes
        after = df.shape[1]
        removed = before - after
        if removed > 0:
            cleaning_log.append(f"Eliminadas {removed} columnas vacías o constantes.")

    # 3. Tratamiento según % de nulos
    for col in df.columns:
        null_pct = df[col].isnull().mean()
        if null_pct > null_threshold:
            df.drop(columns=[col], inplace=True)
            cleaning_log.append(f"Columna '{col}' eliminada (más del {int(null_pct*100)}% de nulos).")
            continue  # ya no está, pasamos a la siguiente

        # Imputación según tipo
        if df[col].dtype in ['float64', 'int64']:
            if strategy_numeric == "mean":
                df[col] = df[col].fillna(df[col].mean())
                cleaning_log.append(f"Columna numérica '{col}' imputada con la media.")
            elif strategy_numeric == "zero":
                df[col] = df[col].fillna(0)
                cleaning_log.append(f"Columna numérica '{col}' imputada con cero.")
            elif strategy_numeric == "drop":
                df = df.dropna(subset=[col])
                cleaning_log.append(f"Filas con nulos en '{col}' eliminadas.")
        elif df[col].dtype == 'object':
            if strategy_categorical == "fill":
                df[col] = df[col].fillna("Desconocido")
                cleaning_log.append(f"Columna categórica '{col}' imputada con 'Desconocido'.")
            elif strategy_categorical == "drop":
                df = df.dropna(subset=[col])
                cleaning_log.append(f"Filas con nulos en '{col}' eliminadas.")

    # 4. Log final con nulos restantes
    total_missing = df.isnull().sum().sum()
    if total_missing > 0:
        cleaning_log.append(f"⚠️ Quedan {int(total_missing)} valores nulos después de limpieza.")

    df.attrs["cleaning_log"] = cleaning_log
    return df
