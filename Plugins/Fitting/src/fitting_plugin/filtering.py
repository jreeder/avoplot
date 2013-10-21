import wx
import csv
import os
import os.path
import math
import scipy
import scipy.optimize
import numpy
import datetime
import time

from scipy.special import erf
from avoplot import plugins, series, controls, subplots
from avoplot.persist import PersistentStorage
from avoplot.plugins import AvoPlotPluginSimple
from avoplot.subplots import AvoPlotXYSubplot
from avoplot.series import XYDataSeries
from collections import namedtuple

from avoplot.gui import widgets

plugin_is_GPL_compatible = True
        
#define new data series type for FTIR data
class DataToFilter(series.XYDataSeries):
    def __init__(self, *args, **kwargs):
        super(DataToFilter, self).__init__(*args, **kwargs)
        
        #add a control for this data series to allow the user to change the 
        #frequency of the wave using a slider.
        self.add_control_panel(FilterPickerCtrl(self))    
    
    @staticmethod
    def get_supported_subplot_type():
        return AvoPlotXYSubplot
    
class FitData(series.XYDataSeries):
    def __init__(self, name, series):
        xdata, ydata = series.get_data()
        fit_x_data, fit_y_data, gaussian_params = fit_gaussian(xdata, ydata)
        super(FitData, self).__init__(name, xdata = fit_x_data, ydata = fit_y_data)
        
        #add a control for this data series to allow the user to change the 
        #frequency of the wave using a slider.
        
        series.get_parent_element().add_data_series(self)
    
    @staticmethod
    def get_supported_subplot_type():
        return AvoPlotXYSubplot


class Filtering(plugins.AvoPlotPluginSimple):
    def __init__(self):
        super(Filtering, self).__init__("Filtering", DataToFilter)
        
        self.set_menu_entry(['Filtering', 'New data series'], "Plot a data series to filter")
        
        
    def plot_into_subplot(self, subplot):
        
        col_data, spectrum_file = self.load_file()
        if col_data is None:
            return False
        
        data_series = DataToFilter('New Series', xdata = col_data[0], ydata = col_data[1])
        subplot.add_data_series(data_series)
        
        data_series = DataToFilter('New Series', xdata = col_data[2], ydata = col_data[3])
        subplot.add_data_series(data_series)
        
        if len(col_data) == 6:
            data_series = DataToFilter('New Series', xdata = col_data[4], ydata = col_data[5])
            subplot.add_data_series(data_series)
        
        #TODO - setting the name here means that the figure gets renamed
        #everytime that a series gets added
        subplot.get_parent_element().set_name(os.path.basename(spectrum_file))
        
        return True
    
    
    
    def load_file(self):
        persist = PersistentStorage()
    
        try:
            last_path_used = persist.get_value("filter_spectra_dir")
        except KeyError:
            last_path_used = ""

        #get filename to open
        spectrum_file = wx.FileSelector("Choose spectrum file to open", 
                                        default_path=last_path_used)
        if spectrum_file == "":
            return None, None
        
        persist.set_value("filter_spectra_dir", os.path.dirname(spectrum_file))
        
        with open(spectrum_file, 'rU') as csvfile:
            reader = csv.reader(csvfile, delimiter='\t')
            
        #reader = csv.reader(open(spectrum_file, "rU"), dialect=csv.excel) 
      
            col_data = []
            
            count = 0
            while count<29:
                next(reader)
                count += 1
            #Skip the first 29 lines, which are header
            
            ncols = len(next(reader))
            #This reads the 28th line, assigns its length to ncols & moves to the next line.
        
            for i in range(ncols):
                col_data.append(([float(x[i]) for x in reader]))
                csvfile.seek(0)
                count = 0
                while count<30:
                    next(reader)
                    count += 1
            #now col_data is a list of lists of column data  
            
            #Make col_data accessible to the rest of the class without needing to call the load_uvvis_file method
            self.col_data = col_data
        
        try:        
            return col_data, spectrum_file

        except Exception,e:
            print e.args
            wx.MessageBox("Unable to load spectrum file \'%s\'. "
                          "Unrecognised file format."%spectrum_file, 
                          "AvoPlot", wx.ICON_ERROR)
            return None


class FilterPickerCtrl(controls.AvoPlotControlPanelBase):
    """
    Control panel where the buttons to draw backgrounds will appear
    """
    def __init__(self, series):
        #call the parent class's __init__ method, passing it the name that we
        #want to appear on the control panels tab.
        super(FilterPickerCtrl, self).__init__("Background Fit")
        
        #store the data series object that this control panel is associated with, 
        #so that we can access it later
        self.series = series
    
    def define_data(self):
        xdata, ydata = self.series.get_data()
        return xdata, ydata

    
    def setup(self, parent):
        super(FilterPickerCtrl, self).setup(parent)
        
        self.axes = self.series.get_parent_element().get_mpl_axes()
        self.xdata, self.ydata = self.define_data()
        
        self.plot_obj = parent
        
        fit_button = wx.Button(self, wx.ID_ANY, "Fit Gaussian")
        self.Add(fit_button, 0, wx.ALIGN_TOP|wx.ALL,border=10)

        wx.EVT_BUTTON(self, fit_button.GetId(), self.fit_gaussian_evt)
        
        self.SetAutoLayout(True)
   
    def fit_gaussian_evt(self, evnt):
        try:
            wx.BeginBusyCursor()
            FitData('Fit Gaussian', self.series)
            #self.peak_height_params = calc_peak_height_pos(self.xdata, fit_y_data)
            
            self.series.update()
        except ValueError, e:
            wx.EndBusyCursor()
            wx.MessageBox( 'Failed to fit gaussian.\nReason:%s'%e.args[0], 'AvoPlot Filtering',wx.ICON_ERROR)
              
        finally:
            wx.EndBusyCursor()
        
GaussianParameters = namedtuple('GaussianParameters',['amplitude','mean','sigma','y_offset'])

def fit_gaussian(xdata, ydata, amplitude_guess=None, mean_guess=None, sigma_guess=None, y_offset_guess=None, plot_fit=True):
    """
    Fits a gaussian to some data using a least squares fit method. Returns a named tuple
    of best fit parameters (amplitude, mean, sigma, y_offset).
     
    Initial guess values for the fit parameters can be specified as kwargs. Otherwise they
    are estimated from the data.
     
    If plot_fit=True then the fit curve is plotted over the top of the raw data and displayed.
    """

    if len(xdata) != len(ydata):
        raise ValueError, "Lengths of xdata and ydata must match"
     
    if len(xdata) < 4:
        raise ValueError, "xdata and ydata need to contain at least 4 elements each"
     
    # guess some fit parameters - unless they were specified as kwargs
    if amplitude_guess is None:
        amplitude_guess = max(ydata)
     
    if mean_guess is None:
        weights = ydata - numpy.average(ydata)
        weights[numpy.where(weights <0)]=0 
        mean_guess = numpy.average(xdata,weights=weights)
                    
    #use the y value furthest from the maximum as a guess of y offset 
    if y_offset_guess is None:
        data_midpoint = (xdata[-1] + xdata[0])/2.0
        if mean_guess > data_midpoint:
            yoffset_guess = ydata[0]        
        else:
            yoffset_guess = ydata[-1]
 
    #find width at half height as estimate of sigma        
    if sigma_guess is None:      
        variance = numpy.dot(numpy.abs(ydata), (xdata-mean_guess)**2)/numpy.abs(ydata).sum()  # Fast and numerically precise    
        sigma_guess = math.sqrt(variance)
     
     
    #put guess params into an array ready for fitting
    p0 = numpy.array([amplitude_guess, mean_guess, sigma_guess, yoffset_guess])
 
    #define the gaussian function and associated error function
    fitfunc = lambda p, x: p[0]*scipy.exp(-(x-p[1])**2/(2.0*p[2]**2)) + p[3]
    errfunc = lambda p, x, y: fitfunc(p,x)-y
    
    # do the fitting
    p1, success = scipy.optimize.leastsq(errfunc, p0, args=(xdata,ydata))
 
    if success not in (1,2,3,4):
        raise RuntimeError, "Could not fit Gaussian to data."
 
    fit_y_data = [fitfunc(p1, i) for i in xdata]
     
    return xdata, fit_y_data, GaussianParameters(*p1)

def calc_peak_height_pos(xdata, ydata):    
    peak_idx = numpy.argmax(ydata)
    global_peak_idx = peak_idx + numpy.argmin(numpy.abs(xdata))
    print "peak index = %d, global index = %d"%(peak_idx, global_peak_idx)
    return xdata[global_peak_idx], ydata[global_peak_idx]
        


plugins.register(Fitting())
