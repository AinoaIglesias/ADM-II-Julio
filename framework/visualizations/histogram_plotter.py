import plotly.express as px
from .base_plotter import BasePlotter

class HistogramPlotter(BasePlotter):
    def plot(self, df, x, y=None, group_col=None):
        fig = px.histogram(df, x=x, color=group_col)
        fig.write_html("output/histogram_plot.html")
        print("✅ Histograma guardado en output/histogram_plot.html")
