import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .base import ChartStrategy
import pandas as pd

class BarChartStrategy(ChartStrategy):
    def plot(self, df, x_col, y_col, buffer, agregacion, grupo=None):
        fig, ax = plt.subplots(figsize=(16, 6), dpi=150)

        if grupo:
            # Tabla “wide” por x_col y grupo
            if agregacion=="Conteo":
                grouped = df.groupby([x_col,grupo]).size().unstack(fill_value=0)
            else:
                func    = {"Media":"mean","Suma":"sum"}[agregacion]
                grouped = df.groupby([x_col,grupo])[y_col].agg(func).unstack(fill_value=0)

            # Top-10 categorías de x_col
            totals = grouped.sum(axis=1)
            top10  = totals.sort_values(ascending=False).head(10).index
            grouped = grouped.loc[top10]

            # Barras lado-a-lado (no apiladas)
            grouped.plot(
                kind="bar",
                stacked=False,
                width=0.8,
                ax=ax
            )
            ax.legend(title=grupo, bbox_to_anchor=(1.05,1), loc="upper left")

        else:
            # Serie simple
            if agregacion=="Conteo":
                series = df.groupby(x_col).size()
            else:
                series = df.groupby(x_col)[y_col].agg(
                    {"Media":"mean","Suma":"sum"}[agregacion]
                )
            top10 = series.sort_values(ascending=False).head(10)
            top10.plot(kind="bar", width=0.8, ax=ax)

        ax.set_xlabel(x_col)
        ax.set_ylabel("Resultado")
        ax.set_title(f"{agregacion} de {y_col} por {x_col}" + (f" (agrupado por {grupo})" if grupo else ""))
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
        plt.tight_layout()

        fig.savefig(buffer, format="png")
        plt.close(fig)
