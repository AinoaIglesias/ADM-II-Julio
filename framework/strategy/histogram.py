import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .base import ChartStrategy
import pandas as pd

class HistogramStrategy(ChartStrategy):
    def plot(self, df, x_col, y_col, buffer, agregacion=None, grupo=None):
        # Para histograma usamos y_col como variable
        data = pd.to_numeric(df[y_col], errors="coerce").dropna()

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(data, bins=30, edgecolor='black', alpha=0.7)
        ax.set_xlabel(y_col)
        ax.set_ylabel("Frecuencia")
        ax.set_title(f"Histograma de {y_col}")
        plt.tight_layout()

        fig.savefig(buffer, format="png")
        plt.close(fig)
