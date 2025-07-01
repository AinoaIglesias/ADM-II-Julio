import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .base import ChartStrategy
import pandas as pd

class BoxplotStrategy(ChartStrategy):
    def plot(self, df, x_col, y_col, buffer, agregacion=None, grupo=None):
        fig, ax = plt.subplots(figsize=(10, 6))

        # Dibujamos el boxplot de la columna y_col
        bp = ax.boxplot(
            df[y_col].dropna(),
            notch=False,
            patch_artist=True,
            labels=[y_col]        # <-- etiqueta para la caja
        )

        ax.set_xlabel(y_col)
        ax.set_ylabel(y_col)
        ax.set_title(f"Boxplot de {y_col}")

        # Aunque con 'labels' bastaría, puedes forzar la leyenda así:
        ax.legend(
            [bp["boxes"][0]],
            [y_col],
            loc='upper right'
        )

        plt.tight_layout()
        fig.savefig(buffer, format="png")
        plt.close(fig)
