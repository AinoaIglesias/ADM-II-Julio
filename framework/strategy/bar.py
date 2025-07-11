import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO
from .base import ChartStrategy
import pandas as pd

class BarChartStrategy(ChartStrategy):
    def plot(self,
             df: pd.DataFrame,
             x_col: str,
             y_col: str,
             agregacion: str,
             grupo: str = None) -> bytes:

        fig, ax = plt.subplots(figsize=(16, 6), dpi=150)

        if grupo:
            # agrupado por x_col + grupo
            df[grupo] = df[grupo].astype(str)
            if agregacion == "Conteo":
                grp = df.groupby([x_col, grupo]).size().unstack(fill_value=0)
            else:
                func = {"Media": "mean", "Suma": "sum"}[agregacion]
                grp = df.groupby([x_col, grupo])[y_col].agg(func).unstack(fill_value=0)

            # Top-10 en x_col
            tops = grp.sum(axis=1).nlargest(10).index
            grp.loc[tops].plot(kind="bar", width=0.8, ax=ax, stacked=False)
            ax.legend(title=grupo, bbox_to_anchor=(1.05, 1), loc="upper left")

        else:
            # serie simple
            if agregacion == "Conteo":
                series = df.groupby(x_col).size()
            else:
                series = df.groupby(x_col)[y_col].agg(
                    {"Media": "mean", "Suma": "sum"}[agregacion]
                )
            series.nlargest(10).plot(kind="bar", width=0.8, ax=ax)

        ax.set_xlabel(x_col)
        ax.set_ylabel("Resultado")
        title = f"{agregacion} de {y_col} por {x_col}"
        if grupo:
            title += f" (agrupado por {grupo})"
        ax.set_title(title)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        plt.tight_layout()

        buf = BytesIO()
        fig.savefig(buf, format="png")
        plt.close(fig)
        return buf.getvalue()
