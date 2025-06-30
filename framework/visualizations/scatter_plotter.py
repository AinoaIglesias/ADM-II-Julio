import plotly.express as px
from .base_plotter import BasePlotter

class ScatterPlotter(BasePlotter):
    def plot(self, df, x, y, group_col=None):
        fig = px.scatter(df, x=x, y=y, color=group_col)
        fig.write_html("output/scatter_plot.html")
        print("✅ Gráfico de dispersión guardado en output/scatter_plot.html")
