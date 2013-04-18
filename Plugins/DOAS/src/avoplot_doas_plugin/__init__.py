from avoplot.plugins import register
from doas_spectrum_plot import DOASSpectrumPlugin
from ratio_time_plot import RatioTimePlugin


#register plugins with AvoPlot so that they are loaded on startup
register(DOASSpectrumPlugin())

register(RatioTimePlugin())
