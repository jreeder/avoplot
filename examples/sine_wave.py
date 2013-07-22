import numpy
from avoplot import plugins, series


plugin_is_GPL_compatible = True


class ExamplePlugin(plugins.AvoPlotPluginSimple):
        def __init__(self):
            super(ExamplePlugin, self).__init__("Example Plugin", 
                                                series.XYDataSeries)
        
            self.set_menu_entry(['Examples','Sine Wave'], 
                                "Plot a sine wave")
        
        
        def plot_into_subplot(self, subplot):
            
            x_data = numpy.linspace(0, 7, 500)
            y_data = numpy.sin(x_data)
            
            data_series = series.XYDataSeries("sine wave", xdata=x_data, 
                                              ydata=y_data)
            
            subplot.add_data_series(data_series)
            
            return True


plugins.register(ExamplePlugin())