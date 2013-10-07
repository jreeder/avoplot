import wx
import csv
import os
import os.path
import math
from scipy.special import erf
import scipy
import scipy.optimize
import numpy
from avoplot import plugins, series, controls, subplots
from avoplot.persist import PersistentStorage
from avoplot.plugins import AvoPlotPluginSimple
from avoplot.subplots import AvoPlotXYSubplot
from avoplot.series import XYDataSeries

from avoplot.gui import widgets

plugin_is_GPL_compatible = True

class FTIRSpectrumSubplot(AvoPlotXYSubplot):
#This is the "subplot" where the spectrum will appear
    def my_init(self):
        ax = self.get_mpl_axes()
        ax.set_xlabel('Wavenumber (cm$^{-1}$)')
        ax.set_ylabel('Absorbance')
        
        self.__inverted_x = False
    
    
    def add_data_series(self, data):
        AvoPlotXYSubplot.add_data_series(self, data)
        
        if not self.__inverted_x:
           self.get_mpl_axes().invert_xaxis()
           self.__inverted_x = True
    
     
        
#define new data series type for FTIR data
class FTIRSpectrumData(series.XYDataSeries):
    def __init__(self, *args, **kwargs):
        super(FTIRSpectrumData, self).__init__(*args, **kwargs)
        
        #add a control for this data series to allow the user to change the 
        #frequency of the wave using a slider.
        self.add_control_panel(BackgroundCalcCtrl(self))    
    
    @staticmethod
    def get_supported_subplot_type():
        return FTIRSpectrumSubplot



class FTIRPlugin(plugins.AvoPlotPluginSimple):
    def __init__(self):
        super(FTIRPlugin, self).__init__("FTIR Plugin Kayla", FTIRSpectrumData)
        
        self.set_menu_entry(['FTIR', 'New Spectrum'], "Plot an FTIR spectrum")
        
        
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
            return wavenumber, absorbance, spectrum_file
        #TODO see return above
        except Exception,e:
            print e.args
            wx.MessageBox("Unable to load spectrum file \'%s\'. "
                          "Unrecognised file format."%spectrum_file, 
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
        self.data = self.series.get_data()
        self.wavenumber = self.data[0]
        self.absorbance = self.data[1]
    
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
        
    
    def set_peak_height(self, height):
        self.peak_height_text.SetLabel("Peak Height:\n%f"%height)
        
    
    def fit_h2o(self, evnt):
        try:
            wx.BeginBusyCursor()
            bkgd = fit_h2o_peak(self.wavenumber, self.absorbance, self.axes, plot_fit=True)
            #bkgd = fit_h2o_peak(self.wavenumber, self.absorbance, ax, plot_fit=True)
            peak_height = calc_h2o_peak_height(self.wavenumber, self.absorbance, bkgd)
            self.set_peak_height(peak_height)
            
            self.series.update()
        except ValueError, e:
            wx.EndBusyCursor()
            wx.MessageBox( 'Failed to find H2O background.\nReason:%s'%e.args[0], 'AvoPlot FTIR',wx.ICON_ERROR)
              
        finally:
            wx.EndBusyCursor()
    
    def create_plot(self):
        self.axes.plot(self.wavenumber, self.absorbance)
        self.axes.set_xlim((self.axes.get_xlim()[1],self.axes.get_xlim()[0]))
        self.axes.set_xlabel("Wavenumber")
        self.axes.set_ylabel("Absorbance")

            
def get_h2o_fitting_points(xdata, ydata, bkgd_func=None, 
                           target_wavenumber_range=200, tolerance=30):
    """
    This function finds (target_wavenumber_range +- tolerance) number of points
    from either side of the H2O peak. The points are selected from after the 
    minima on either side of the peak.
    
    The H2O peak is searched for between 3000-4000 cm-1 wavenumber.
    
    The bkgd_func arg can be used to subtract a global background from the 
    data before the points are searched for - this can be useful for very skewed
    spectra. If the function can't find the fitting points without a 
    background function, then it calls itself again passing get_global_bkgd as
    the bkgd_func argument.
    """
    
    #initialise the cropping limits (these are in wavenumber)
    l_crop = 2200
    peak_l_crop = 3000
    r_crop = 4000
    
    #make a copy of the original data, so that we have an uncropped version
    master_xdata = numpy.array(xdata)
    master_ydata = numpy.array(ydata)   
    
    #crop the data to the correct size 
    data_mask = numpy.where(numpy.logical_and(master_xdata > l_crop, master_xdata <=r_crop))
    xdata = master_xdata[data_mask]
    ydata = master_ydata[data_mask]
    
    #find where the H2O peak is
    mask = numpy.where(xdata > peak_l_crop)
    peak_idx = numpy.argmax(ydata[mask]) + mask[0][0]
    
    print "H2O peak found at ",xdata[peak_idx]
    
    #find the minima either side of the peak
    l_min = numpy.argmin(ydata[:peak_idx])
    r_min = numpy.argmin(ydata[peak_idx:])+peak_idx
    
    print "l_min = ",xdata[l_min], "r_min = ", xdata[r_min]
    
    #now identify approximately the right number of points beyond
    #each minimum such that we have     
    while (abs(xdata[l_min]-l_crop - target_wavenumber_range) > tolerance or
          abs(r_crop - xdata[r_min] - target_wavenumber_range) > tolerance):
        
        l_crop -= target_wavenumber_range - (xdata[l_min]-l_crop)
        r_crop -= (r_crop - xdata[r_min]) - target_wavenumber_range
        
        data_mask = numpy.where(numpy.logical_and(master_xdata > l_crop, 
                                                  master_xdata <=r_crop))
        xdata = master_xdata[data_mask]
        ydata = master_ydata[data_mask]
           
        mask = numpy.where(xdata > peak_l_crop)
        peak_idx = numpy.argmax(ydata[mask]) + mask[0][0]
        
        if bkgd_func is None:
            if len(ydata[:peak_idx])>0:
                l_min = numpy.argmin(ydata[:peak_idx])
            else:
                l_min = 0
                break
        else:
            l_min = numpy.argmin(ydata[:peak_idx]-bkgd_func(xdata[:peak_idx]))
        r_min = numpy.argmin(ydata[peak_idx:])+peak_idx
        
        print "l_min = ",xdata[l_min], "r_min = ", xdata[r_min]
        print "l_crop = ",l_crop, "r_crop = ", r_crop, "\n"
    
    if xdata[l_min] < 2000:
        if bkgd_func is not None:
            raise ValueError("Could not find low wavenumber minimum.")
        print "calling again with bkgd_func"
        return get_h2o_fitting_points(master_xdata, master_ydata, bkgd_func=get_global_bkgd(master_xdata, master_ydata))
    
    if xdata[r_min] > 5000:  
         raise ValueError("Could not find high wavenumber minimum.")
     
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
    
    
    
    

#class FTIRSpecPlot(PlotPanelBase):
#    
#    def __init__(self, parent, filename):            
#        self.wavenumber, self.absorbance = load_ftir_file(filename)        
#        print classify_spectrum(self.wavenumber, self.absorbance)
#        PlotPanelBase.__init__(self,parent, os.path.basename(filename))
#        self.control_panel = FTIRFittingPanel(self, classify_spectrum(self.wavenumber, self.absorbance))
#        self.h_sizer.Insert(0,self.control_panel, flag=wx.ALIGN_LEFT)
#        
#        self.create_plot()
#        
#    
#    def fit_h2o(self, evnt):
#        try:
#            wx.BeginBusyCursor()
#            bkgd = fit_h2o_peak(self.wavenumber, self.absorbance, self.axes, plot_fit=True)
#            peak_height = calc_h2o_peak_height(self.wavenumber, self.absorbance, bkgd)
#            self.control_panel.set_peak_height(peak_height)
#            
#            self.canvas.draw()
#            self.canvas.gui_repaint()
#        finally:
#            wx.EndBusyCursor()
#    
#    def create_plot(self):
#        self.axes.plot(self.wavenumber, self.absorbance)
#        self.axes.set_xlim((self.axes.get_xlim()[1],self.axes.get_xlim()[0]))
#        self.axes.set_xlabel("Wavenumber")
#        self.axes.set_ylabel("Absorbance")


plugins.register(FTIRPlugin())
