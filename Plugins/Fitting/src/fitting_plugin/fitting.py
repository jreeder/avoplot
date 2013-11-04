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
class DataToFit(series.XYDataSeries):
    def __init__(self, *args, **kwargs):
        super(DataToFit, self).__init__(*args, **kwargs)

        self.add_control_panel(FitPickerCtrl(self))    
    
    @staticmethod
    def get_supported_subplot_type():
        return AvoPlotXYSubplot
    
class FitData(series.XYDataSeries):
    def __init__(self, series):
        xdata, ydata = series.get_data()
        fit_x_data, fit_y_data, gaussian_params = fit_gaussian(xdata, ydata)
        super(FitData, self).__init__(series.get_name() + ' Fit', xdata = fit_x_data, ydata = fit_y_data)
        
        self.add_control_panel(FitDataCtrl(self))
        
        series.add_subseries(self)
    
    @staticmethod
    def get_supported_subplot_type():
        return AvoPlotXYSubplot


class Fitting(plugins.AvoPlotPluginSimple):
    def __init__(self):
        super(Fitting, self).__init__("Fitting", DataToFit)
        
        self.set_menu_entry(['Fitting', 'New data series'], "Plot a data series to fit")
        
        
    def plot_into_subplot(self, subplot):
        
        col_data, spectrum_file, col_headers = self.load_file()
        if col_data is None:
            return False
        
        data_series = DataToFit(col_headers[1], xdata = col_data[0], ydata = col_data[1])
        subplot.add_data_series(data_series)
        
        data_series = DataToFit(col_headers[3], xdata = col_data[2], ydata = col_data[3])
        subplot.add_data_series(data_series)
        
        if len(col_data) == 6:
            data_series = DataToFit(col_headers[5], xdata = col_data[4], ydata = col_data[5])
            subplot.add_data_series(data_series)
        
        #TODO - setting the name here means that the figure gets renamed
        #everytime that a series gets added
        subplot.get_parent_element().set_name(os.path.basename(spectrum_file))
        
        return True
    
    
    
    def load_file(self):
        persist = PersistentStorage()
    
        try:
            last_path_used = persist.get_value("fit_spectra_dir")
        except KeyError:
            last_path_used = ""

        #get filename to open
        spectrum_file = wx.FileSelector("Choose spectrum file to open", 
                                        default_path=last_path_used)
        if spectrum_file == "":
            return None, None
        
        persist.set_value("fit_spectra_dir", os.path.dirname(spectrum_file))
        
        with open(spectrum_file, 'rU') as csvfile:
            reader = csv.reader(csvfile, delimiter='\t')
            
        #reader = csv.reader(open(spectrum_file, "rU"), dialect=csv.excel) 
      
            col_data = []
            
            count = 0
            while count<29:
                next(reader)
                count += 1
            #Skip the first 29 lines, which are header
            
            col_headers = next(reader)
            
            ncols = len(col_headers)
        
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
            return col_data, spectrum_file, col_headers

        except Exception,e:
            print e.args
            wx.MessageBox("Unable to load spectrum file \'%s\'. "
                          "Unrecognised file format."%spectrum_file, 
                          "AvoPlot", wx.ICON_ERROR)
            return None


class FitPickerCtrl(controls.AvoPlotControlPanelBase):
    """
    Control panel where the buttons to draw backgrounds will appear
    """
    def __init__(self, series):
        #call the parent class's __init__ method, passing it the name that we
        #want to appear on the control panels tab.
        super(FitPickerCtrl, self).__init__("Background Fit")
        
        #store the data series object that this control panel is associated with, 
        #so that we can access it later
        self.series = series
    
    def define_data(self):
        xdata, ydata = self.series.get_data()
        return xdata, ydata

    
    def setup(self, parent):
        super(FitPickerCtrl, self).setup(parent)
        
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
            FitData(self.series)
            #self.peak_height_params = calc_peak_height_pos(self.xdata, fit_y_data)
            
            self.series.update()
        except ValueError, e:
            wx.EndBusyCursor()
            wx.MessageBox( 'Failed to fit gaussian.\nReason:%s'%e.args[0], 'AvoPlot Fitting',wx.ICON_ERROR)
              
        finally:
            wx.EndBusyCursor()
            
class FitDataCtrl(controls.AvoPlotControlPanelBase):
    """
    Control panel where the buttons to draw backgrounds will appear
    """
    def __init__(self, series):
        #call the parent class's __init__ method, passing it the name that we
        #want to appear on the control panels tab.
        super(FitDataCtrl, self).__init__("Fit Parameters")
        
        #store the data series object that this control panel is associated with, 
        #so that we can access it later
        self.series = series
    
    def define_data(self):
        xdata, ydata = self.series.get_data()
        fit_x_data, fit_y_data, gaussian_params = fit_gaussian(xdata, ydata)
        return fit_x_data, fit_y_data, gaussian_params
    
    def setup(self, parent):
        super(FitDataCtrl, self).setup(parent)
        
        fit_x_data, fit_y_data, gaussian_params = self.define_data()
        
        label_text = wx.StaticText(self, -1, "Gaussian Parameters:")
        amplitude_text = wx.StaticText(self, -1, "Amplitude: " + str(gaussian_params.amplitude))
        mean_text = wx.StaticText(self, -1, "Mean: " + str(gaussian_params.mean))
        sigma_text = wx.StaticText(self, -1, "Sigma: " + str(gaussian_params.sigma))
        y_offset_text = wx.StaticText(self, -1, "Y Offset: " + str(gaussian_params.y_offset))
        
        self.Add(label_text, 0, wx.ALIGN_TOP|wx.ALL,border=10)
        self.Add(amplitude_text, 0, wx.ALIGN_TOP|wx.ALL,border=5)
        self.Add(mean_text, 0, wx.ALIGN_TOP|wx.ALL,border=5)
        self.Add(sigma_text, 0, wx.ALIGN_TOP|wx.ALL,border=5)
        self.Add(y_offset_text, 0, wx.ALIGN_TOP|wx.ALL,border=5)
        
        save_button = wx.Button(self, wx.ID_ANY, "Save Mean Params")
        self.Add(save_button, 0, wx.ALIGN_TOP|wx.ALL,border=10)

        wx.EVT_BUTTON(self, save_button.GetId(), self.save_button_evt)
        
        self.SetAutoLayout(True)
    
    def save_button_evt(self, evnt):
        fit_x_data, fit_y_data, gaussian_params = self.define_data()
        with open('/home/ki247/Params/params.csv', 'a') as csvfile:
            params_file = csv.writer(csvfile)
            params_file.writerow([str(self.series.get_parent_element().get_parent_element().get_parent_element().get_name()) + ' ' + str(self.series.get_name())])
            params_file.writerow([str(gaussian_params.mean)])
        
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


plugins.register(Fitting())
