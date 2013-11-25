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
import os
import numpy
from datetime import datetime
from matplotlib.widgets import SpanSelector

import math
import scipy.optimize
import collections

from avoplot.subplots import AvoPlotXYSubplot
from avoplot import controls
from avoplot import core
from avoplot import subplots
from avoplot import figure
from avoplot.gui import linestyle_editor
from avoplot.persist import PersistentStorage


class DataSeriesBase(core.AvoPlotElementBase):
    """
    Base class for all data series.
    """
    
    def __init__(self, name):
        super(DataSeriesBase, self).__init__(name)
        self.__plotted = False
        self._mpl_lines = []
    
    
    def get_mpl_lines(self):
        """
        Returns a list of matplotlib line objects associated with the data 
        series.
        """
        assert self.__plotted, ('Data series must be plotted before you can '
                                'access the matplotlib lines')
        return self._mpl_lines
    
    
    def get_figure(self):
        """
        Returns the AvoPlot figure (avoplot.figure.AvoPlotFigure) object that
        the series is contained within, or None if the series does not yet 
        belong to a figure.
        """
        #look up the list of parents recursively until we find a figure object
        parent = self.get_parent_element()
        while not isinstance(parent, figure.AvoPlotFigure):
            if parent is None:
                return None
            parent = parent.get_parent_element()
            
            #sanity check - there should always be a figure object somewhere
            #in the ancestry of a series object.
            if isinstance(parent, core.AvoPlotSession):
                raise RuntimeError("Reached the root element before an "
                                   "AvoPlotFigure instance was found.")
        return parent
    
    
    def get_subplot(self):
        """
        Returns the AvoPlot subplot (subclass of 
        avoplot.subplots.AvoPlotSubplotBase) object that
        the series is contained within, or None if the series does not yet 
        belong to a subplot.
        """
        #look up the list of parents recursively until we find a figure object
        parent = self.get_parent_element()
        while not isinstance(parent, subplots.AvoPlotSubplotBase):
            if parent is None:
                return None
            parent = parent.get_parent_element()
            
            #sanity check - there should always be a figure object somewhere
            #in the ancestry of a series object.
            if isinstance(parent, core.AvoPlotSession):
                raise RuntimeError("Reached the root element before an "
                                   "AvoPlotFigure instance was found.")
        return parent
        
    
    def delete(self):
        """
        Overrides the base class method in order to remove the line(s) from the 
        axes and draw the changes. 
        """
        self._mpl_lines.pop(0).remove()
        self.update()
        super(DataSeriesBase, self).delete()        
        
        
    def _plot(self, subplot):
        """
        Called in subplot.add_data_series() to plot the data into the subplot
        and setup the controls for the series (the parent of the series is not
        known until it gets added to the subplot)
        """
        assert not self.__plotted, ('plot() should only be called once')
        
        self.__plotted = True
        
        self._mpl_lines = self.plot(subplot)
        self.setup_controls(subplot.get_figure())
    
    
    def add_subseries(self, series):
        """
        Adds a series as a child of this series. Normally you would expect 
        series to be parented by subplots, however, for things like fit-lines 
        it makes more sense for them to be associated with the series that they
        are fitting then the subplot that they are plotted in.
        
        series must be an instance of avoplot.series.DataSeriesBase or subclass
        thereof.
        """
        assert isinstance(series, DataSeriesBase), ("Expecting series object of "
                                                    "type DataSeriesBase.")
        series.set_parent_element(self)
        series._plot(self.get_subplot())
    
    
    def update(self):
        """
        Redraws the series.
        """
        subplot = self.get_subplot()
        if subplot: #subplot could be None - in which case do nothing
            subplot.update()
    
    
    def plot(self, subplot):
        """
        Plots the data series into the specified subplot (AvoPlotSubplotBase 
        instance) and returns the list of matplotlib lines associated with the 
        series. This method should be overridden by subclasses.
        """
        return []
    
    
    def preprocess(self, *args):
        """
        Runs any preprocessing required on the data and returns it. This 
        should be overridden by subclasses.
        """
        #return the data passed in unchanged
        return args
    
    
    def is_plotted(self):
        """
        Returns True if the series has already been plotted. False otherwise.
        """
        return self.__plotted   



class XYDataSeries(DataSeriesBase):
    """
    Class to represent 2D XY data series.
    """
    def __init__(self, name, xdata=None, ydata=None):
        super(XYDataSeries, self).__init__(name)
        self.set_xy_data(xdata, ydata)
        self.add_control_panel(XYSeriesControls(self))
        #self.add_control_panel(XYSeriesFittingControls(self))
          
          
    @staticmethod    
    def get_supported_subplot_type():
        """
        Static method that returns the class of subplot that the data series
        can be plotted into. This will be a subclass of AvoPlotSubplotBase.
        """
        return AvoPlotXYSubplot
    
    
    def set_xy_data(self, xdata=None, ydata=None):
        """
        Sets the x and y values of the data series. Note that you need to call
        the update() method to draw the changes to the screen.
        """
        if xdata is None and ydata is None:
            xdata = numpy.array([])
            ydata = numpy.array([])
            
        elif xdata is None:
            xdata = numpy.arange(len(ydata))
            
        elif ydata is None:
            ydata = numpy.arange(len(xdata))
            
        else:
            assert len(xdata) == len(ydata)
        
        self.__xdata = xdata
        self.__ydata = ydata
        
        if self.is_plotted():
            #update the the data in the plotted line
            line, = self.get_mpl_lines()
            line.set_data(*self.preprocess(self.__xdata, self.__ydata))
    
    
    def get_raw_data(self):
        """
        Returns a tuple (xdata, ydata) of the raw data held by the series 
        (without any pre-processing operations performed). In general you should
        use the get_data() method instead.
        """
        return (self.__xdata, self.__ydata)
    
    
    def get_data(self):
        """
        Returns a tuple (xdata, ydata) of the data held by the series, with
        any pre-processing operations applied to it.
        """
        return self.preprocess(self.__xdata.copy(), self.__ydata.copy())
    
    
    def preprocess(self, xdata, ydata):
        """
        Runs any required preprocessing operations on the x and y data and
        returns them.
        """
        xdata, ydata = super(XYDataSeries, self).preprocess(xdata, ydata)
        return xdata, ydata
        
    
    def plot(self, subplot):
        """
        plots the x,y data into the subplot as a line plot.
        """
        return subplot.get_mpl_axes().plot(*self.get_data())
    
    
    def export(self):
        """
        Exports the selected data series. Called when user right clicks on the data series (see nav_panel.py).
        """
        persistant_storage = PersistentStorage()
        
        try:
            last_path_used = persistant_storage.get_value("series_export_last_dir_used")
        except KeyError:
            last_path_used = ""
            
        export_dialog = wx.FileDialog(None, message="Export data series as...",
                                       defaultDir=last_path_used, defaultFile="AvoPlot Series.txt",
                                       style=wx.SAVE|wx.FD_OVERWRITE_PROMPT, wildcard = "TXT files (*.txt)|*.txt")
        
        if export_dialog.ShowModal() == wx.ID_OK:
            path = export_dialog.GetPath()
            persistant_storage.set_value("series_export_last_dir_used", os.path.dirname(path))
            xdata, ydata = self.get_data()
            
            with open(path, 'w') as fp:
                for i in range(len(xdata)):
                    if isinstance(xdata[0], datetime):
                        fp.write("%s\t%f\n" %(str(xdata[i]), ydata[i]))
                        #yfloat = []
                        #for i in ydata:
                        #    yfloat.append(time.mktime(ydata[i].timetuple()))
                        #fp.write("%f\t%f\n" %(xdata[i], yfloat[i]))
                    else:
                        fp.write("%f\t%f\n" %(xdata[i], ydata[i]))

        
        export_dialog.Destroy()            



class XYSeriesControls(controls.AvoPlotControlPanelBase):
    """
    Control panel to allow user editing of data series (line styles,
    colours etc.)
    """
    
    def __init__(self, series):
        super(XYSeriesControls, self).__init__("Series")
        self.series = series
        
               
    def setup(self, parent):
        """
        Creates all the controls in the panel
        """
        super(XYSeriesControls, self).setup(parent)
        mpl_lines = self.series.get_mpl_lines()
        
        #explicitly set the the marker colour to its existing value, otherwise
        #it will get changed if we change the line colour
        mpl_lines[0].set_markeredgecolor(mpl_lines[0].get_markeredgecolor())
        mpl_lines[0].set_markerfacecolor(mpl_lines[0].get_markerfacecolor())
        
        #add line controls
        line_ctrls_static_szr = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, 'Line'), wx.VERTICAL)
        self.linestyle_ctrl_panel = linestyle_editor.LineStyleEditorPanel(self, mpl_lines, self.series.update)
        line_ctrls_static_szr.Add(self.linestyle_ctrl_panel, 0, wx.ALIGN_TOP | wx.ALIGN_RIGHT)
       
        #add the marker controls
        marker_ctrls_static_szr = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, 'Markers'), wx.VERTICAL)
        self.marker_ctrls_panel =  linestyle_editor.MarkerStyleEditorPanel(self, mpl_lines, self.series.update)      
        marker_ctrls_static_szr.Add(self.marker_ctrls_panel, 0, wx.ALIGN_TOP | wx.ALIGN_RIGHT)
        
        #add the controls to the control panel's internal sizer
        self.Add(line_ctrls_static_szr,0,wx.EXPAND|wx.ALL, border=5)
        self.Add(marker_ctrls_static_szr,0,wx.EXPAND|wx.ALL, border=5)    
        
        
        line_ctrls_static_szr.Layout()

    def on_display(self):
        
        self.marker_ctrls_panel.SendSizeEvent()
        self.linestyle_ctrl_panel.SendSizeEvent()


################################################################
#
#  Everything below here is experimental and under development!
#
#
################################################################

class XYSeriesFittingControls(controls.AvoPlotControlPanelBase):
    def __init__(self, series):
        super(XYSeriesFittingControls, self).__init__("Fitting")
        self.series = series
    
    def setup(self, parent):
        """
        Creates all the controls in the panel
        """
        super(XYSeriesFittingControls, self).setup(parent)
        
        select_button = wx.Button(self, -1, "Select")
        self.Add(select_button)
        wx.EVT_BUTTON(self, select_button.GetId(), self.on_select)
        
        self.min_txt = wx.StaticText(self, -1, "Min: ")
        self.max_txt = wx.StaticText(self, -1, "Max: ")
        
        
        
        self.Add(self.min_txt)
        self.Add(self.max_txt)
        
        fit_button = wx.Button(self, -1, "Fit")
        self.Add(fit_button)
        wx.EVT_BUTTON(self, fit_button.GetId(), self.on_fit)
        
        self.span = None
    
    def on_select(self, evnt):
        ax = self.series.get_subplot().get_mpl_axes()
        if self.span is None:
            self.span = SpanSelector(ax, self.onselect, 'horizontal', useblit=True)
        else:
            self.span.visible = True
            
    def on_fit(self, evnt):
        x,y = self.series.get_data()
        min_idx = numpy.where(x >= self.min_selection)[0][0]
        max_idx = numpy.where(x <= self.max_selection)[0][-1]
        
        fit_x_data, fit_y_data, gaussian_params = fit_gaussian(x[min_idx:max_idx], y[min_idx:max_idx])
        
        FitData(self.series, fit_x_data, fit_y_data, gaussian_params)
        
    def onselect(self, vmin, vmax):
        self.min_selection = vmin
        self.max_selection = vmax
        self.min_txt.SetLabel("Min: %s"%(self.min_selection))
        self.max_txt.SetLabel("Max: %s"%(self.max_selection))
        self.span.visible = False

class FitData(XYDataSeries):
    def __init__(self, s, xdata, ydata, gaussian_params):
        super(FitData, self).__init__(s.get_name() + ' Fit', xdata, ydata)
        self.gaussian_params = gaussian_params
        self.add_control_panel(FitDataCtrl(self))
        
        s.add_subseries(self)
    
    @staticmethod
    def get_supported_subplot_type():
        return AvoPlotXYSubplot
    
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
        
        self.gaussian_params = series.gaussian_params
    
    
    def setup(self, parent):
        super(FitDataCtrl, self).setup(parent)
        
        gaussian_params = self.gaussian_params
        
        label_text = wx.StaticText(self, -1, "Gaussian Parameters:")
        amplitude_text = wx.StaticText(self, -1, "Amplitude: " + str(gaussian_params.amplitude))
        mean_text = wx.StaticText(self, -1, "Mean: " + str(gaussian_params.mean))
        sigma_text = wx.StaticText(self, -1, "Sigma: " + str(gaussian_params.sigma))
        fwhm_text = wx.StaticText(self, -1, "FWHM: " + str(2.0 * math.sqrt(2.0 * math.log(2.0)) *gaussian_params.sigma))
        y_offset_text = wx.StaticText(self, -1, "Y Offset: " + str(gaussian_params.y_offset))
        
        self.Add(label_text, 0, wx.ALIGN_TOP|wx.ALL,border=10)
        self.Add(amplitude_text, 0, wx.ALIGN_TOP|wx.ALL,border=5)
        self.Add(mean_text, 0, wx.ALIGN_TOP|wx.ALL,border=5)
        self.Add(sigma_text, 0, wx.ALIGN_TOP|wx.ALL,border=5)
        self.Add(fwhm_text, 0, wx.ALIGN_TOP|wx.ALL,border=5)
        self.Add(y_offset_text, 0, wx.ALIGN_TOP|wx.ALL,border=5)

GaussianParameters = collections.namedtuple('GaussianParameters',['amplitude','mean','sigma','y_offset'])

        
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
    fitfunc = lambda p, x: p[0]*numpy.exp(-(x-p[1])**2/(2.0*p[2]**2)) + p[3]
    errfunc = lambda p, x, y: fitfunc(p,x)-y
    
    # do the fitting
    p1, success = scipy.optimize.leastsq(errfunc, p0, args=(xdata,ydata))
 
    if success not in (1,2,3,4):
        raise RuntimeError, "Could not fit Gaussian to data."
    
    xdata = numpy.linspace(xdata[0], xdata[-1], 2000)
    fit_y_data = [fitfunc(p1, i) for i in xdata]
     
    return xdata, fit_y_data, GaussianParameters(*p1)   
        