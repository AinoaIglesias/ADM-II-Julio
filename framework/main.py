from datasources.csv_source import CSVDataSource
from visualizations.bar_plotter import BarPlotter
from visualizations.line_plotter import LinePlotter
from visualizations.histogram_plotter import HistogramPlotter
from visualizations.scatter_plotter import ScatterPlotter

import os
os.makedirs("output", exist_ok=True)


# CONFIGURA AQUÍ TU DATASET
#filepath = "C:/Users/ainoa/OneDrive/Desktop/ADM-II-Julio/datasets/madrid_2001_2018_calidad_aire.csv"
filepath = "C:/Users/ainoa/OneDrive/Desktop/ADM-II-Julio/datasets/US_Accidents_March23.csv"
source = CSVDataSource(filepath)
df = source.load()

print("🔍 Columnas:", df.columns.tolist())
print(df.describe(include='all'))

# CONFIGURA QUÉ VISUALIZAR
# Dataset: calidad del aire
x = "date"
y = "CO"
group = "station"


print("📊 Mostrando gráficas...")

BarPlotter().plot(df, x, y, group)
LinePlotter().plot(df, x, y, group)
HistogramPlotter().plot(df, x, None, group)
ScatterPlotter().plot(df, x, y, group)
