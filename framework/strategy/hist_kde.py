import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .base import ChartStrategy
import pandas as pd

class HistogramKDEStrategy(ChartStrategy):
    def plot(self, df, x_col, y_col, buffer, agregacion=None, grupo=None):
        # 1) Extraemos y limpiamos la serie
        data = pd.to_numeric(df[y_col], errors="coerce").dropna()

        # 2) Recortamos fuera de percentiles 1–99 para evitar outliers extremos
        low, high = data.quantile(0.01), data.quantile(0.99)
        data = data[(data >= low) & (data <= high)]

        # 3) Creación de la figura
        fig, ax = plt.subplots(figsize=(10, 6))

        # 4) Histograma (density=True para compararlo con KDE)
        ax.hist(
            data,
            bins=20,
            density=True,
            alpha=0.6,
            edgecolor='black',
            label='Histograma'
        )

        # 5) Curva KDE
        data.plot(
            kind='kde',
            ax=ax,
            label='KDE',
            linewidth=2
        )

        # 6) Etiquetas y leyenda
        ax.set_xlabel(y_col)
        ax.set_ylabel("Densidad")
        ax.set_title(f"Histograma + KDE de {y_col}")
        ax.legend(loc='best')
        ax.grid(True, linestyle='--', alpha=0.5)

        plt.tight_layout()
        fig.savefig(buffer, format="png")
        plt.close(fig)
