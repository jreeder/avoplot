import wx
import os.path

from avoplot.persist import PersistantStorage
from avoplot.gui.plots import PlotPanelBase
from avoplot.plugins import AvoPlotPluginBase
from doas.spectrum_loader import SpectrumIO, UnableToLoad


class DOASSpectrumPlot(PlotPanelBase):
    
    def __init__(self, parent, filename):
               
        loader = SpectrumIO()        
        self.spectrum = loader.load(filename)        
        
        PlotPanelBase.__init__(self,parent)
        self.create_plot()
    
    
    def create_plot(self):
        self.axes.plot(self.spectrum.wavelengths, self.spectrum.counts)



class DOASSpectrumPlugin(AvoPlotPluginBase):
    
    def __init__(self):
        AvoPlotPluginBase.__init__(self, "DOAS Spectrum")
    
    
    def get_onNew_handler(self):
        return ("DOAS", "DOAS Spectrum", "Plot a DOAS spectrum", self.plot_doas_spectrum)
    
    
    def plot_doas_spectrum(self, evnt):
        
        persist = PersistantStorage()
        
        try:
            last_path_used = persist.get_value("doas_spectra_dir")
        except KeyError:
            last_path_used = ""
        
        #get filename to open
        spectrum_file = wx.FileSelector("Choose spectrum file to open", default_path=last_path_used)
        if spectrum_file == "":
            return
        
        persist.set_value("doas_spectra_dir", os.path.dirname(spectrum_file))
        
        try:
            spec_plot = DOASSpectrumPlot(self.get_parent(), spectrum_file)
        except UnableToLoad:
            wx.MessageBox("Unable to load spectrum file \'%s\'. Unrecognised file format."%spectrum_file, "AvoPlot", wx.ICON_ERROR)
            return
        
        self.add_plot_to_main_window(spec_plot, os.path.basename(spectrum_file))
        
    