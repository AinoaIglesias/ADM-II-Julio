# framework/strategy/line.py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO
from .base import ChartStrategy
import pandas as pd

class LineChartStrategy(ChartStrategy):
    def plot(self,
             df: pd.DataFrame,
             x_col: str,
             y_col: str,
             agregacion: str,
             grupo: str = None) -> bytes:

        fig, ax = plt.subplots(figsize=(16, 6), dpi=150)

        if grupo:
            # pivot por x_col + grupo
            if agregacion == "Conteo":
                tmp = (
                    df.groupby([x_col, grupo])
                      .size()
                      .rename("count")
                      .reset_index()
                )
                pivot = tmp.pivot(index=x_col, columns=grupo, values="count")
            else:
                func = {"Media": "mean", "Suma": "sum"}[agregacion]
                pivot = df.pivot_table(
                    index=x_col, columns=grupo, values=y_col, aggfunc=func
                )

            pivot = pivot.sort_index()
            for col in pivot.columns:
                s = pivot[col].dropna()
                ax.plot(s.index.astype(str), s.values, marker='o', label=str(col))

            plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
            ncol = 3 if len(pivot.columns) > 15 else 1
            ax.legend(title=grupo, bbox_to_anchor=(1.02, 1), loc="upper left", ncol=ncol)

        else:
            # serie única
            if agregacion == "Conteo":
                serie = df.groupby(x_col).size().rename("count")
                label = "count"
            else:
                func = {"Media": "mean", "Suma": "sum"}[agregacion]
                serie = df.groupby(x_col)[y_col].agg(func)
                label = y_col

            ax.plot(serie.index.astype(str), serie.values, marker='o', label=label)
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
            ax.legend()

        ax.set_xlabel(x_col)
        ax.set_ylabel("Resultado")
        title = f"{agregacion} de {y_col if y_col else 'registros'} por {x_col}"
        if grupo:
            title += f" (agrupado por {grupo})"
        ax.set_title(title)
        plt.tight_layout()

        buf = BytesIO()
        fig.savefig(buf, format="png")
        plt.close(fig)
        return buf.getvalue()
