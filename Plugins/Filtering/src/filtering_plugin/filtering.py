import wx
import csv
import os
import os.path
import math
import pandas as pd
import scipy
import scipy.optimize
import numpy
import datetime
import time
import pandas

from scipy.special import erf
from avoplot import plugins, series, controls, subplots
from avoplot.persist import PersistentStorage
from avoplot.plugins import AvoPlotPluginSimple
from avoplot.subplots import AvoPlotXYSubplot
from avoplot.series import XYDataSeries

from avoplot.gui import widgets

plugin_is_GPL_compatible = True

class FilteringSubplot(AvoPlotXYSubplot):
#This is the "subplot" where the spectrum will appear
    def my_init(self):
        ax = self.get_mpl_axes()
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
    
    
    def add_data_series(self, data):
        AvoPlotXYSubplot.add_data_series(self, data)    
     
        
#define new data series type for FTIR data
class DataToFilter(series.XYDataSeries):
    def __init__(self, *args, **kwargs):
        super(DataToFilter, self).__init__(*args, **kwargs)
        
        #add a control for this data series to allow the user to change the 
        #frequency of the wave using a slider.
        self.add_control_panel(FilterPickerCtrl(self))    
    
    @staticmethod
    def get_supported_subplot_type():
        return FilteringSubplot



class Filtering(plugins.AvoPlotPluginSimple):
    def __init__(self):
        super(Filtering, self).__init__("Filtering", DataToFilter)
        
        self.set_menu_entry(['Filtering', 'New data series'], "Plot a data series to filter")
        
        
    def plot_into_subplot(self, subplot):
        
        wavenumber, absorbance, spectrum_file = self.load_ftir_file()
        if wavenumber is None:
            return False
        
        data_series = FTIRSpectrumData(os.path.basename(spectrum_file), 
                                       xdata=wavenumber, 
                                       ydata=absorbance)
        
        subplot.add_data_series(data_series)
        
        #TODO - setting the name here means that the figure gets renamed
        #everytime that a series gets added
        subplot.get_parent_element().set_name(os.path.basename(spectrum_file))
        
        return True
    
    
    
    def load_file(self):
        persist = PersistentStorage()
    
        try:
            last_path_used = persist.get_value("file_dir")
        except KeyError:
            last_path_used = ""

        #get filename to open
        file = wx.FileSelector("Choose file to open", 
                                        default_path=last_path_used)
        if file == "":
            return None
        
        persist.set_value("file_dir", os.path.dirname(file))
        
        reader = csv.reader(open(file, "rb"), delimiter='\t') 
        
        xdata = []
        ydata = []
    
        for line in reader:
            xdata.append(line[0])
            ydata.append(float(line[1]))
        
        if isinstance(xdata[0], datetime):
            xdata = dates.date2num(xdata)      
        
        try:        
            return xdata, ydata, file

        except Exception,e:
            print e.args
            wx.MessageBox("Unable to load spectrum file \'%s\'. "
                          "Unrecognised file format."%file, 
                          "AvoPlot", wx.ICON_ERROR)
            return None


#Start Extra Control Panel Functions -- created after adv_sine_wave example in AvoPlot documentation
class BackgroundCalcCtrl(controls.AvoPlotControlPanelBase):
    """
    Control panel where the buttons to draw backgrounds will appear
    """
    def __init__(self, series):
        #call the parent class's __init__ method, passing it the name that we
        #want to appear on the control panels tab.
        super(BackgroundCalcCtrl, self).__init__("Background Fit")
        
        #store the data series object that this control panel is associated with, 
        #so that we can access it later
        self.series = series
    
    def define_data(self):
        wavenumber = self.wavenumber
        absorbance = self.absorbance
        return wavenumber, absorbance

    
    def setup(self, parent):
        super(BackgroundCalcCtrl, self).setup(parent)
        
        #AvoPlotXYSubplot is a class, not an object/instance so you can't do this!
        #also get_mpl_axes is a method - so you would need () to make this do what you intended
        #self.axes = AvoPlotXYSubplot.get_mpl_axes
        self.axes = self.series.get_parent_element().get_mpl_axes()
        
        self.plot_obj = parent
        spec_type = classify_spectrum
        
        h2o_button = wx.Button(self, wx.ID_ANY, "Fit H2O")
        self.peak_height_text = wx.StaticText(self, -1, "Peak Height:\n")
        self.Add(self.peak_height_text)
        self.Add(h2o_button, 0, wx.ALIGN_TOP|wx.ALL,border=10)
#        sizer = wx.StaticText(self, -1, "Spec Type:\n%s"%spec_type, 0, wx.ALIGN_TOP|wx.ALL)
#        sizer_peak_height = wx.sizer(self.peak_height_text,0,wx.ALIGN_TOP|wx.ALL)
#        self.Add(sizer)
#        self.Add(sizer_peak_height)
        wx.EVT_BUTTON(self, h2o_button.GetId(), self.fit_h2o)
        
#        self.SetSizer(sizer)
#        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        


plugins.register(Filtering())
