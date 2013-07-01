#Copyright (C) Nial Peters 2013
#
#This file is part of AvoPlot.
#
#AvoPlot is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#AvoPlot is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with AvoPlot.  If not, see <http://www.gnu.org/licenses/>.

import wx
import os.path

from avoplot.persist import PersistentStorage
from avoplot.plugins import AvoPlotPluginSimple
from avoplot.subplots import AvoPlotXYSubplot
from avoplot.series import XYDataSeries

from doas.spectrum_loader import SpectrumIO, UnableToLoad

plugin_is_GPL_compatible = True

class DOASSpectrumSubplot(AvoPlotXYSubplot):
    def my_init(self):
        ax = self.get_mpl_axes()
        ax.set_xlabel('Wavelength (nm)')
        ax.set_ylabel('Counts')
    

#define new data series type for DOAS data
class DOASSpectrumData(XYDataSeries):
    @staticmethod
    def get_supported_subplot_type():
        return DOASSpectrumSubplot


class DOASSpectrumPlugin(AvoPlotPluginSimple):
    def __init__(self):
        AvoPlotPluginSimple.__init__(self,"DOAS Spectrum Plugin", DOASSpectrumData)
        
        self.set_menu_entry(['DOAS','DOAS Spectrum'], "Plot a DOAS Spectrum file")
    
    
    def plot_into_subplot(self, subplot):
        spec = self.load_spectrum()
        if spec is None:
            return False
        
        data_series = DOASSpectrumData(os.path.basename(spec.filename),xdata=spec.wavelengths, ydata=spec.counts)
        
        subplot.add_data_series(data_series)
        
        return True
    
    
    def load_spectrum(self):
        persist = PersistentStorage()
        
        try:
            last_path_used = persist.get_value("doas_spectra_dir")
        except KeyError:
            last_path_used = ""
        
        #get filename to open
        spectrum_file = wx.FileSelector("Choose spectrum file to open", default_path=last_path_used)
        if spectrum_file == "":
            return None
        
        persist.set_value("doas_spectra_dir", os.path.dirname(spectrum_file))
        
        loader = SpectrumIO()
        try:        
            return loader.load(spectrum_file)
        except Exception,e:
            print e.args
            wx.MessageBox("Unable to load spectrum file \'%s\'. Unrecognised file format."%spectrum_file, "AvoPlot", wx.ICON_ERROR)
            return False
