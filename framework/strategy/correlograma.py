import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .base import ChartStrategy
import pandas as pd

class CorrelogramaStrategy(ChartStrategy):
    def plot(self, df, x_col, y_col, buffer, agregacion=None, grupo=None):
        """
        Dibuja la matriz de correlación (heatmap) de todas las columnas numéricas.
        """
        # seleccionamos sólo columnas numéricas
        num_df = df.select_dtypes(include=["number"])
        corr = num_df.corr()

        fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
        cax = ax.matshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
        fig.colorbar(cax, fraction=0.046, pad=0.04)

        ticks = range(len(corr.columns))
        ax.set_xticks(ticks)
        ax.set_yticks(ticks)
        ax.set_xticklabels(corr.columns, rotation=90)
        ax.set_yticklabels(corr.columns)

        ax.set_title("Mmatriz de correlación", pad=20)
        plt.tight_layout()
        fig.savefig(buffer, format="png")
        plt.close(fig)
