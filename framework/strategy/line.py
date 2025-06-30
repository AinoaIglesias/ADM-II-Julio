import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .base import ChartStrategy
import pandas as pd

class LineChartStrategy(ChartStrategy):
    def plot(self, df, x_col, y_col, buffer, agregacion, grupo=None):
        fig, ax = plt.subplots(figsize=(16, 6), dpi=150)

        if grupo:
            # 1) Creamos el pivot
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
                    index=x_col,
                    columns=grupo,
                    values=y_col,
                    aggfunc=func
                )

            # 2) Ordenamos el eje X y NO hacemos fillna
            pivot = pivot.sort_index()

            # 3) Dibujamos cada serie sólo con sus valores existentes
            for estacion in pivot.columns:
                serie = pivot[estacion].dropna()
                ax.plot(
                    serie.index.astype(str),
                    serie.values,
                    marker='o',
                    linewidth=1,
                    label=str(estacion),
                )

            # 4) Ajustamos ticks y leyenda
            ax.set_xticks(pivot.index.astype(str))
            ax.set_xticklabels(pivot.index.astype(str), rotation=45, ha='right')
            ncols = 3 if len(pivot.columns) > 15 else 1
            ax.legend(
                title=grupo,
                bbox_to_anchor=(1.02, 1),
                loc="upper left",
                fontsize="small",
                ncol=ncols
            )

        else:
            # Serie única (directa, media o suma)
            if agregacion == "Conteo":
                serie = df.groupby(x_col).size().rename("count")
                x_vals = serie.index.astype(str)
                y_vals = serie.values
                label  = "count"
            else:
                func   = {"Media": "mean", "Suma": "sum"}[agregacion]
                serie  = df.groupby(x_col)[y_col].agg(func)
                x_vals = serie.index.astype(str)
                y_vals = serie.values
                label  = y_col

            ax.plot(x_vals, y_vals, marker='o', linewidth=1, label=label)
            ax.set_xticks(x_vals)
            ax.set_xticklabels(x_vals, rotation=45, ha='right')
            ax.legend()

        ax.set_xlabel(x_col)
        ax.set_ylabel("Resultado")
        title = f"{agregacion} de {y_col if y_col else 'registros'} por {x_col}"
        if grupo:
            title += f" (agrupado por {grupo})"
        ax.set_title(title)
        plt.tight_layout()

        fig.savefig(buffer, format="png")
        plt.close(fig)
