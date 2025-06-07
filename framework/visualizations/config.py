from strategy import (
    ColumnBarCount,
    ColumnHistogram,
    LinePlotMonthlyByYear,
    LinePlotTimeMean
)

# Ruta al dataset
DATA_PATH = "data/processed/accidents_clean.csv"

# Lista de estrategias (independiente del dataset)
VISUALIZATIONS = [
    ColumnBarCount(column="State"),
    ColumnHistogram(column="Temperature(F)"),
    ColumnHistogram(column="Humidity(%)"),
    LinePlotMonthlyByYear(datetime_column="Start_Time"),
    LinePlotTimeMean(datetime_column="Start_Time", value_column="Temperature(F)", frequency="D")
]
