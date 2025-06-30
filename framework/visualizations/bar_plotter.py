import plotly.express as px
from .base_plotter import BasePlotter

class BarPlotter(BasePlotter):
    def plot(self, df, x, y, group_col=None):
        fig = px.bar(df, x=x, y=y, color=group_col, barmode='group' if group_col else 'relative')
        fig.write_html("output/bar_plot.html")
        print("✅ Gráfico de barras guardado en output/bar_plot.html")
