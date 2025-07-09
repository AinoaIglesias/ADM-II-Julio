import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO
from .base import ChartStrategy
import pandas as pd

class BoxplotStrategy(ChartStrategy):
    def plot(self,
             df: pd.DataFrame,
             y_col: str,
             grupo: str = None,
             **kwargs) -> bytes:

        fig, ax = plt.subplots(figsize=(10, 6))
        bp = ax.boxplot(
            df[y_col].dropna(),
            notch=False,
            patch_artist=True,
            labels=[y_col]
        )

        ax.set_xlabel(y_col)
        ax.set_ylabel(y_col)
        ax.set_title(f"Boxplot de {y_col}")
        ax.legend([bp["boxes"][0]], [y_col], loc='upper right')
        plt.tight_layout()

        buf = BytesIO()
        fig.savefig(buf, format="png")
        plt.close(fig)
        return buf.getvalue()
