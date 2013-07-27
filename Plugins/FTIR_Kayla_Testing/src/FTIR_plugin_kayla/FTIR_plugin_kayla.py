import numpy
import csv
import os
import os.path
import math
from avoplot import plugins, series

plugin_is_GPL_compatible = True


def load_ftir_file(filename):
    reader = csv.reader(open(filename, "rb"), dialect="excel") 

    wavenumber = []
    absorbance = []

    for line in reader:
        wavenumber.append(float(line[0]))
        absorbance.append(float(line[1]))
    
    return wavenumber, absorbance


class FTIRPlugin(plugins.AvoPlotPluginBase):
    def __init__(self):
        super(FTIRPlugin, self).__init__("FTIR Plugin Kayla", series.XYDataSeries)
        
        self.set_menu_entry(['FTIR'], "Plot an FTIR spectrum")
    
    
    def plot_into_subplot(self, subplot, filename):
        self.wavenumber, self.absorbance = load_ftir_file(filename) 
        
        x_data = self.wavenumber
        y_data = self.absorbance
        
        data_series = series.XYDataSeries("FTIR Spectrum", xdata=x_data, ydata=y_data)
        
        subplot.add_data_series(data_series)
        
        return True

plugins.register(FTIRPlugin())
