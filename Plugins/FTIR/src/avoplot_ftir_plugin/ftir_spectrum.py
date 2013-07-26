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
import csv
import os
import os.path
import math
from scipy.special import erf
import scipy
import scipy.optimize
import numpy

from avoplot import plugins, series #new-version update

from avoplot.gui.plots import PlotPanelBase
from avoplot.plugins import AvoPlotPluginBase
from avoplot.persist import PersistentStorage

plugin_is_GPL_compatible = True #new-version update

def load_ftir_file(filename):
    reader = csv.reader(open(filename, "rb"), dialect="excel") 

    wavenumber = []
    absorbance = []

    for line in reader:
        wavenumber.append(float(line[0]))
        absorbance.append(float(line[1]))
    
    return wavenumber, absorbance


#Start new-version Class updates 

class FTIRPlugin(plugins.AvoPlotPluginBase):        
    def __init__(self, parent, filename): 
        super(FTIRPlugin, self).__init__("FTIR Plugin", series.DataSeriesBase)
        
        self.set_menu_entry(['New FTIR Spectrum'])
    
    def plot_into_subplot(self, subplot):
        PlotPanelBase.__init__(self, parent, os.path.basename(filename))
        self.control_panel = FTIRFittingPanel(self, classify_spectrum(self.wavenumber, self.absorbance))
        self.h_sizer.Insert(0,self.control_panel, flag=wx.ALIGN_LEFT)
        
        self.wavenumber, self.absorbance = load_ftir_file(filename)   
        
        x_data = self.wavenumber
        y_data = self.absorbance 
        
        data_series = series.DataSeriesBase("FTIR Spectra", xdata=x_data, ydata=y_data)
        
        subplot.add_data_series(data_series)
        
        return True
    
plugins.register(FTIRPlugin())

#End new-version Class updates


class FTIRFittingPanel(wx.Panel):
    def __init__(self, parent, spec_type):
        self.plot_obj = parent
        wx.Panel.__init__(self, parent, wx.ID_ANY,style=wx.BORDER_SIMPLE)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        h2o_button = wx.Button(self, wx.ID_ANY, "Fit H2O")
        self.peak_height_text = wx.StaticText(self, -1, "Peak Height:\n")
        sizer.Add(h2o_button, 0, wx.ALIGN_TOP|wx.ALL,border=10)
        sizer.Add(wx.StaticText(self, -1, "Spec Type:\n%s"%spec_type), 0, wx.ALIGN_TOP|wx.ALL,border=10)
        sizer.Add(self.peak_height_text,0, wx.ALIGN_TOP|wx.ALL,border=10)
        wx.EVT_BUTTON(self, h2o_button.GetId(), parent.fit_h2o)
        
        self.SetSizer(sizer)
        sizer.Fit(self)
        self.SetAutoLayout(True)
    
    def set_peak_height(self, height):
        self.peak_height_text.SetLabel("Peak Height:\n%f"%height)
            
#def fit_h2o_peak(xdata, ydata, axes, amplitude_guess=None, mean_guess=None, sigma_guess=None, y_offset_guess=None, plot_fit=False):
#    """
#    Fits a gaussian to some data using a least squares fit method. Returns a named tuple
#    of best fit parameters (amplitude, mean, sigma, y_offset).
#    
#    Initial guess values for the fit parameters can be specified as kwargs. Otherwise they
#    are estimated from the data.
#    
#    If plot_fit=True then the fit curve is plotted over the top of the raw data and displayed.
#    """
#    
#    master_xdata = numpy.array(xdata)
#    master_ydata = numpy.array(ydata)
#    
#    if len(xdata) != len(ydata):
#        raise ValueError, "Lengths of xdata and ydata must match"
#    
#    #crop the x and y data to the fitting range
#    data_mask = numpy.where(numpy.logical_and(master_xdata > 2500, master_xdata <=4000))
#    xdata = master_xdata[data_mask]
#    ydata = master_ydata[data_mask]
#    
#    # guess some fit parameters - unless they were specified as kwargs
#    if amplitude_guess is None:
#        amplitude_guess = max(ydata)
#    
#    if mean_guess is None:
#        weights = ydata - numpy.average(ydata)
#        weights[numpy.where(weights <0)]=0 
#        mean_guess = numpy.average(xdata,weights=weights)
#                   
#    skew_guess = 5.0 #TODO - do this properly
#    
#    #use the y value furthest from the maximum as a guess of y offset 
#    intercept_guess = ydata[0]
#    
#    grad_guess = (ydata[-1]-ydata[0]) / (xdata[-1] - xdata[0])
#
#    #find width at half height as estimate of sigma        
#    if sigma_guess is None:      
#        variance = numpy.dot(numpy.abs(ydata), (xdata-mean_guess)**2)/numpy.abs(ydata).sum()  # Fast and numerically precise    
#        sigma_guess = math.sqrt(variance)
#    x3_guess = -1.0
#    x2_guess = -1.0
#    #put guess params into an array ready for fitting
#    p0 = numpy.array([amplitude_guess, mean_guess, sigma_guess, skew_guess, grad_guess,intercept_guess])
#
#    #define the gaussian function and associated error function
#    gaussian_func = lambda p, x: p[0]*scipy.exp(-(x-p[1])**2/(2.0*p[2]**2))
#    skew_func = lambda x: 0.5 * (1.0 + erf(x/math.sqrt(2.0)))
#    
#    fitfunc = lambda p,x: gaussian_func(p,x) * skew_func(p[3] * ((x - p[1])/p[2])) +p[4]*x + p[5]
#    errfunc = lambda p, x, y: fitfunc(p,x)-y
#   
#    # do the fitting
#    p1, success = scipy.optimize.leastsq(errfunc, p0, args=(xdata,ydata))
#    
#    print "p0 = ",p0
#    print "p1 = ",p1
#
#    if success not in (1,2,3,4):
#        raise RuntimeError, "Could not fit Gaussian to data."
#
#    if plot_fit:
#        axes.plot( xdata,[fitfunc(p1, i) for i in xdata], 'r-', label='fit')
#        axes.plot(xdata, [i*p1[4] + p1[5] for i in xdata], 'g-', label='bkgd')
#        axes.legend()

def get_h2o_fitting_points(xdata, ydata, bkgd_func=None, target_wavenumber_range=200, tolerance=30):
    
    #initialise the cropping limits
    l_crop = 2200
    r_crop = 4000
    
    master_xdata = numpy.array(xdata)
    master_ydata = numpy.array(ydata)   
     
    data_mask = numpy.where(numpy.logical_and(master_xdata > l_crop, master_xdata <=r_crop))
    xdata = master_xdata[data_mask]
    ydata = master_ydata[data_mask]
       
    peak_idx = numpy.argmax(ydata)
    
    l_min = numpy.argmin(ydata[:peak_idx])
    r_min = numpy.argmin(ydata[peak_idx:])+peak_idx
        
    while (abs(xdata[l_min]-l_crop - target_wavenumber_range) > tolerance or
          abs(r_crop - xdata[r_min] - target_wavenumber_range) > tolerance):
        
        l_crop -= target_wavenumber_range - (xdata[l_min]-l_crop)
        r_crop -= (r_crop - xdata[r_min]) - target_wavenumber_range
        
        data_mask = numpy.where(numpy.logical_and(master_xdata > l_crop, master_xdata <=r_crop))
        xdata = master_xdata[data_mask]
        ydata = master_ydata[data_mask]
           
        peak_idx = numpy.argmax(ydata)
        
        if bkgd_func is None:
            if len(ydata[:peak_idx])>0:
                l_min = numpy.argmin(ydata[:peak_idx])
            else:
                l_min = 0
                break
        else:
            l_min = numpy.argmin(ydata[:peak_idx]-bkgd_func(xdata[:peak_idx]))
        r_min = numpy.argmin(ydata[peak_idx:])+peak_idx
    
    if xdata[l_min] < 2000:
        if bkgd_func is not None:
            raise ValueError("Failed to find fitting points")
        return get_h2o_fitting_points(master_xdata, master_ydata, bkgd_func=get_global_bkgd(xdata, ydata))
        
    fit_xdata = numpy.concatenate((xdata[:l_min],xdata[r_min:]))
    fit_ydata = numpy.concatenate((ydata[:l_min],ydata[r_min:]))
    return fit_xdata, fit_ydata


def classify_spectrum(xdata, ydata):
    
    #first find the water peak
    l_crop = 2200
    r_crop = 4000
    
    master_xdata = numpy.array(xdata)
    master_ydata = numpy.array(ydata)   
     
    data_mask = numpy.where(numpy.logical_and(master_xdata > l_crop, master_xdata <=r_crop))
    xdata = master_xdata[data_mask]
    ydata = master_ydata[data_mask]
       
    peak_idx = numpy.argmax(ydata)
    global_peak_idx = peak_idx + numpy.argmin(master_xdata-l_crop)
    
    #now find the global minimum
    min_y_idx = numpy.argmin(master_ydata[:global_peak_idx])
    min_y_xvalue = master_xdata[min_y_idx]
    r_min_idx = numpy.argmin(ydata[peak_idx:])+peak_idx
    
    rh_fit_line_param = numpy.polyfit(xdata[r_min_idx:], ydata[r_min_idx:],1)
    rh_fit_line=numpy.poly1d(rh_fit_line_param)
    if rh_fit_line(min_y_xvalue) < master_ydata[min_y_idx]:
        return "Well behaved"
    else:
        return "Low H2O"
    


def get_global_bkgd(xdata, ydata):
    master_xdata = numpy.array(xdata)
    master_ydata = numpy.array(ydata)
    line_grad = numpy.gradient(numpy.array(ydata[numpy.argmax(ydata):]))
    mask = numpy.where(line_grad > 0)
    first_min = ydata[mask[0][0]+numpy.argmax(ydata)]
    print "first min at ",xdata[mask[0][0]]
    
    data_mask = numpy.where(numpy.logical_and(master_xdata > 2200, master_xdata <=4000))
    #xdata = master_xdata[data_mask]
    #ydata = master_ydata[data_mask]
    last_val = master_ydata[-1]
    
    polyfit_params = numpy.polyfit(numpy.array([xdata[mask[0][0]],xdata[-1]]), numpy.array([first_min, last_val]), 1)
    print "polyfit params = ",polyfit_params
    if polyfit_params[0] < 0:
        print "returning zeros as backgrounds"
        return lambda x: numpy.zeros_like(x)
    
    return numpy.poly1d(polyfit_params)
    
    

def fit_h2o_peak(xdata, ydata, axes, plot_fit=True):
    #master_xdata = numpy.array(xdata)
    #master_ydata = numpy.array(ydata)
    #plot(master_xdata, master_ydata)
    if len(xdata) != len(ydata):
        raise ValueError, "Lengths of xdata and ydata must match"
    
    #crop the x and y data to the fitting range
    fit_xdata, fit_ydata = get_h2o_fitting_points(xdata, ydata)
    fit_ydata = fit_ydata
    
    polyfit_params = numpy.polyfit(fit_xdata, fit_ydata, 3)
    bkgd_function = numpy.poly1d(polyfit_params)
    
    axes.plot(fit_xdata,fit_ydata,'+')
    bkgd_xdata = numpy.arange(fit_xdata[0], fit_xdata[-1])
    axes.plot(bkgd_xdata, bkgd_function(bkgd_xdata))
    
    return bkgd_function


def calc_h2o_peak_height(xdata, ydata, bkgd_func):
    l_crop = 2200
    r_crop = 4000
    
    master_xdata = numpy.array(xdata)
    master_ydata = numpy.array(ydata)   
     
    data_mask = numpy.where(numpy.logical_and(master_xdata > l_crop, master_xdata <=r_crop))
    xdata = master_xdata[data_mask]
    ydata = master_ydata[data_mask]
    peak_idx = numpy.argmax(ydata)
    global_peak_idx = peak_idx + numpy.argmin(numpy.abs(master_xdata-l_crop))
    print "peak index = %d, global index = %d"%(peak_idx, global_peak_idx)
    return master_ydata[global_peak_idx] - bkgd_func(master_xdata[global_peak_idx])
    
    
    
    

class FTIRSpecPlot(PlotPanelBase):
    
    def __init__(self, parent, filename):            
        self.wavenumber, self.absorbance = load_ftir_file(filename)        
        #print classify_spectrum(self.wavenumber, self.absorbance)
        PlotPanelBase.__init__(self,parent, os.path.basename(filename))
        self.control_panel = FTIRFittingPanel(self, classify_spectrum(self.wavenumber, self.absorbance))
        self.h_sizer.Insert(0,self.control_panel, flag=wx.ALIGN_LEFT)
        
        self.create_plot()
        
    
    def fit_h2o(self, evnt):
        try:
            wx.BeginBusyCursor()
            bkgd = fit_h2o_peak(self.wavenumber, self.absorbance, self.axes, plot_fit=True)
            peak_height = calc_h2o_peak_height(self.wavenumber, self.absorbance, bkgd)
            self.control_panel.set_peak_height(peak_height)
            
            self.canvas.draw()
            self.canvas.gui_repaint()
        finally:
            wx.EndBusyCursor()
    
    def create_plot(self):
        self.axes.plot(self.wavenumber, self.absorbance)
        self.axes.set_xlim((self.axes.get_xlim()[1],self.axes.get_xlim()[0]))
        self.axes.set_xlabel("Wavenumber")
        self.axes.set_ylabel("Absorbance")


class FTIRSpectrumPlugin(AvoPlotPluginBase):
    
    def __init__(self):
        AvoPlotPluginBase.__init__(self, "FTIR Spectrum")
    
    
    def get_onNew_handler(self):
        return ("FTIR", "FTIR Spectrum", "Analyse a single FTIR spectrum", self.open_ftir_spectrum)
    
    
    def open_ftir_spectrum(self, evnt):
        
        persist = PersistentStorage()
        
        try:
            last_path_used = persist.get_value("ftir.spectra_dir")
        except KeyError:
            last_path_used = ""
        
        #get filename to open
        spectrum_file = wx.FileSelector("Choose FTIR spectrum file to open", default_path=last_path_used)
        if spectrum_file == "":
            return
        
        persist.set_value("ftir.spectra_dir", os.path.dirname(spectrum_file))
        
        self.add_plot_to_main_window(FTIRSpecPlot(self.get_parent(), spectrum_file))
        