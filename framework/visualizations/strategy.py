from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

class VisualizationStrategy(ABC):
    def __init__(self, **kwargs):
        self.params = kwargs

    @abstractmethod
    def visualize(self, df: pd.DataFrame):
        pass

class ColumnBarCount(VisualizationStrategy):
    def visualize(self, df):
        col = self.params.get("column")
        if col in df:
            counts = df[col].value_counts().head(10)
            counts.plot(kind='bar', title=f'{col} - Top 10')
            plt.xlabel(col)
            plt.ylabel('Frecuencia')
            plt.tight_layout()
            plt.show()
        else:
            print(f"❌ Columna '{col}' no encontrada.")

class ColumnHistogram(VisualizationStrategy):
    def visualize(self, df):
        col = self.params.get("column")
        if col in df:
            sns.histplot(df[col].dropna(), kde=False, bins=20)
            plt.title(f'Histograma de {col}')
            plt.xlabel(col)
            plt.ylabel('Frecuencia')
            plt.tight_layout()
            plt.show()
        else:
            print(f"❌ Columna '{col}' no encontrada.")


class LinePlotMonthlyByYear(VisualizationStrategy):
    def visualize(self, df):
        time_col = self.params.get("datetime_column")
        if time_col not in df:
            print(f"❌ Columna temporal '{time_col}' no encontrada.")
            return

        df = df.copy()
        df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
        df = df.dropna(subset=[time_col])
        df['year'] = df[time_col].dt.year
        df['month'] = df[time_col].dt.month

        monthly = df.groupby(['month', 'year']).size().unstack().sort_index()

        monthly.plot(marker='o', figsize=(12, 6))
        plt.title("Accidentes por mes, por año")
        plt.xlabel("Mes")
        plt.ylabel("Número de accidentes")
        plt.xticks(ticks=range(1, 13), labels=[
            'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
            'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'
        ])
        plt.legend(title="Año", bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True)
        plt.tight_layout()
        plt.show()

class LinePlotTimeMean(VisualizationStrategy):
    def visualize(self, df):
        time_col = self.params.get("datetime_column")
        value_col = self.params.get("value_column")
        if time_col not in df or value_col not in df:
            print(f"❌ Columnas '{time_col}' o '{value_col}' no encontradas.")
            return

        df = df.copy()
        df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
        df = df.dropna(subset=[time_col, value_col])
        df.set_index(time_col, inplace=True)

        freq = self.params.get("frequency", "D")
        grouped = df[value_col].resample(freq).mean()

        plt.figure(figsize=(12, 6))
        plt.plot(grouped.index, grouped.values)
        plt.title(f"{value_col} - media por {freq}")
        plt.xlabel("Fecha")
        plt.ylabel(value_col)
        plt.grid(True)
        plt.tight_layout()
        plt.show()
