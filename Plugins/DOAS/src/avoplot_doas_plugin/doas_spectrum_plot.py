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
from avoplot import controls

from doas.io import SpectrumIO, UnableToLoad

plugin_is_GPL_compatible = True


class DOASSpectrumControlPanel(controls.AvoPlotControlPanelBase):
    def __init__(self, series):
        
        self.series = series
        super(DOASSpectrumControlPanel, self).__init__('DOAS')
    
    
    def setup(self, parent):
        
        super(DOASSpectrumControlPanel, self).setup(parent)
        
        normalise_button = wx.Button(self, wx.ID_ANY,"Normalise")
        
        wx.EVT_BUTTON(self, normalise_button.GetId(), self.on_normalise)
        
        self.Add(normalise_button,0,wx.ALIGN_CENTER)
    
    
    def on_normalise(self, evnt):
        self.series.normalise_intensities()
        self.series.update()


class DOASSpectrumSubplot(AvoPlotXYSubplot):
    def my_init(self):
        ax = self.get_mpl_axes()
        ax.set_xlabel('Wavelength (nm)')
        ax.set_ylabel('Counts')
    

#define new data series type for DOAS data
class DOASSpectrumData(XYDataSeries):
    def __init__(self, *args, **kwargs):
        super(DOASSpectrumData, self).__init__(*args, **kwargs)
        self.add_control_panel(DOASSpectrumControlPanel(self))
        
    @staticmethod
    def get_supported_subplot_type():
        return DOASSpectrumSubplot
    
    def normalise_intensities(self):
        """
        Rescales all the intensities such that the maximum is at 65535 and the 
        minimum is at 0. This overwrites the original y-data of the series and 
        is therefore NOT a reversible operation.
        """
        x,y = self.get_raw_data()
        y = y - y.min()
        y = (y / y.max()) * 65535
        self.set_xy_data(x, y)


class DOASSpectrumPlugin(AvoPlotPluginSimple):
    def __init__(self):
        AvoPlotPluginSimple.__init__(self,"DOAS Spectrum Plugin", DOASSpectrumData)
        
        self.set_menu_entry(['DOAS','DOAS Spectrum'], "Plot a DOAS Spectrum file")
    
    
    def plot_into_subplot(self, subplot):
        loaded_spectra = self.load_spectrum_files()
        
        if not loaded_spectra:
            return False
        
        for spec in loaded_spectra:
            data_series = DOASSpectrumData(os.path.basename(spec.filename),
                                           xdata=spec.wavelengths, 
                                           ydata=spec.counts)
            
            subplot.add_data_series(data_series)
        
        return True
    
    
    def load_spectrum_files(self):
        persist = PersistentStorage()
        
        try:
            last_path_used = persist.get_value("doas_spectra_dir")
        except KeyError:
            last_path_used = ""
        
        #get filename to open
        fd = wx.FileDialog(self.get_parent(), "Choose spectrum file(s) to open", 
                           defaultDir=last_path_used, style=wx.FD_MULTIPLE | wx.FD_OPEN)
        
        if fd.ShowModal() != wx.ID_OK:
            return []
        
        spectrum_files = fd.GetPaths()
        
        if not spectrum_files:
            return []
        
        persist.set_value("doas_spectra_dir", os.path.dirname(spectrum_files[0]))
        
        loader = SpectrumIO()
        spectra = []
        for filename in spectrum_files:
            try:        
                spectra.append(loader.load(filename))
            except Exception,e:
                print e.args
                wx.MessageBox("Unable to load spectrum file \'%s\'. "
                              "Unrecognised file format."%filename, 
                              "AvoPlot", wx.ICON_ERROR)
        return spectra
