import numpy
import wx
import csv
import os
import os.path
import math
from avoplot import plugins, series
from avoplot.persist import PersistentStorage
from avoplot.plugins import AvoPlotPluginSimple
from avoplot.subplots import AvoPlotXYSubplot
from avoplot.series import XYDataSeries

from doas.spectrum_loader import SpectrumIO, UnableToLoad

plugin_is_GPL_compatible = True

class FTIRSpectrumSubplot(AvoPlotXYSubplot):
    def my_init(self):
        ax = self.get_mpl_axes()
        ax.set_xlabel('Wavenumber (cm-1)')
        ax.set_ylabel('Absorbance')
        
#define new data series type for FTIR data
class FTIRSpectrumData(XYDataSeries):
    @staticmethod
    def get_supported_subplot_type():
        return FTIRSpectrumSubplot



class FTIRPlugin(plugins.AvoPlotPluginSimple):
    def __init__(self):
        super(FTIRPlugin, self).__init__("FTIR Plugin Kayla", FTIRSpectrumData)
        
        self.set_menu_entry(['FTIR', 'New Spectrum'], "Plot an FTIR spectrum")
        
        
    def plot_into_subplot(self, subplot):
        spec = self.load_ftir_file()
        if spec is None:
            return False
        
        data_series = FTIRSpectrumData(os.path.basename(spec.filename), 
                                       xdata=spec.wavenumber, 
                                       ydata=spec.absorbance)
        
        subplot.add_data_series(data_series)
        
        return True
    
    
    
    def load_ftir_file(self):
        persist = PersistentStorage()

        try:
            last_path_used = persist.get_value("ftir_spectra_dir")
        except KeyError:
            last_path_used = ""
        
        #get filename to open
        spectrum_file = wx.FileSelector("Choose spectrum file to open", 
                                        default_path=last_path_used)
        if spectrum_file == "":
            return None
        
        persist.set_value("ftir_spectra_dir", os.path.dirname(spectrum_file))
        
        reader = csv.reader(open(spectrum_file, "rb"), dialect="excel") 
        
        wavenumber = []
        absorbance = []

        for line in reader:
             wavenumber.append(float(line[0]))
             absorbance.append(float(line[1]))        
        
        try:        
            return wavenumber, absorbance
        except Exception,e:
            print e.args
            wx.MessageBox("Unable to load spectrum file \'%s\'. "
                          "Unrecognised file format."%spectrum_file, 
                          "AvoPlot", wx.ICON_ERROR)
            return None


plugins.register(FTIRPlugin())
