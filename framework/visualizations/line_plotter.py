import plotly.express as px
from .base_plotter import BasePlotter

class LinePlotter(BasePlotter):
    def plot(self, df, x, y, group_col=None):
        fig = px.line(df, x=x, y=y, color=group_col)
        fig.write_html("output/line_plot.html")
        print("✅ Gráfico de líneas guardado en output/line_plot.html")
