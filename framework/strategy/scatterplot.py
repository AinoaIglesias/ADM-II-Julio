import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .base import ChartStrategy
import pandas as pd

class ScatterStrategy(ChartStrategy):
    def plot(self, df, x_col, y_col, buffer, agregacion=None, grupo=None):
        fig, ax = plt.subplots(figsize=(10, 6))

        if grupo:
            for g, sub in df.groupby(grupo):
                ax.scatter(
                    sub[x_col],
                    sub[y_col],
                    label=str(g),
                    alpha=0.7,
                    s=20
                )
            ax.legend(title=grupo, bbox_to_anchor=(1.02,1), loc="upper left", fontsize="small")
        else:
            ax.scatter(df[x_col], df[y_col], alpha=0.7, s=20)

        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f"Scatter de {y_col} vs {x_col}")
        plt.tight_layout()

        fig.savefig(buffer, format="png")
        plt.close(fig)
