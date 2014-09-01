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

import math
import scipy.optimize
import collections

from avoplot.subplots import AvoPlotXYSubplot
from avoplot import controls
from avoplot import core
from avoplot import subplots
from avoplot import figure
from avoplot import fitting
from avoplot import data_selection
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
        #self.setup_controls(subplot.get_figure())
    
    
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
        self.add_control_panel(XYSeriesFittingControls(self))
          
          
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
        the update() method to draw the changes to the screen. Note that xdata 
        and ydata may be masked arrays (numpy.ma.masked_array) but only the 
        unmasked values will be stored.
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
        
        #if either of the arrays are masked - then skip the masked values
        if numpy.ma.is_masked(xdata):
            xmask = xdata.mask
        else:
            xmask = numpy.zeros(len(xdata))
            
        if numpy.ma.is_masked(ydata):
            ymask = ydata.mask
        else:
            ymask = numpy.zeros(len(ydata))
        
        data_mask = numpy.logical_not(numpy.logical_or(xmask, ymask))
        data_idxs = numpy.where(data_mask)
        self.__xdata = numpy.array(xdata)[data_idxs]
        self.__ydata = numpy.array(ydata)[data_idxs]
        
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



class FitDataSeries(XYDataSeries):
    def __init__(self, s, xdata, ydata, fit_params):
        super(FitDataSeries, self).__init__(s.get_name() + ' Fit', xdata, ydata)
        self.fit_params = fit_params
        self.add_control_panel(FitParamsCtrl(self))
        
        s.add_subseries(self)
    
    @staticmethod
    def get_supported_subplot_type():
        return AvoPlotXYSubplot

class FitParamsCtrl(controls.AvoPlotControlPanelBase):
    """
    Control panel to display the best fit parameters of a FitDataSeries
    """
    def __init__(self, series):
        #call the parent class's __init__ method, passing it the name that we
        #want to appear on the control panels tab.
        super(FitParamsCtrl, self).__init__("Fit Parameters")
        
        #store the data series object that this control panel is associated with, 
        #so that we can access it later
        self.series = series
        
        self.fit_params = series.fit_params
    
    
    def setup(self, parent):
        super(FitParamsCtrl, self).setup(parent)
        
        label_text = wx.StaticText(self, -1, self.fit_params[0][0]+':')
        self.Add(label_text, 0, wx.ALIGN_TOP|wx.ALL,border=10)
        
        for name, value in self.fit_params[1:]:
            label_text = wx.StaticText(self, -1, ''.join(["   ",name,": ","%0.3e"%value]))
            self.Add(label_text, 0, wx.ALIGN_TOP|wx.ALL,border=5)
        
        
    


class XYSeriesFittingControls(controls.AvoPlotControlPanelBase):
    def __init__(self, series):
        super(XYSeriesFittingControls, self).__init__("Fitting")
        self.series = series
        self.__current_tool_idx = 0
    
    def setup(self, parent):
        """
        Creates all the controls in the panel
        """
        super(XYSeriesFittingControls, self).setup(parent)
        
        data_selection_static_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, 'Fit range'), wx.VERTICAL)
        
        self.selection_panel = data_selection.DataRangeSelectionPanel(self, self.series)
        
        data_selection_static_sizer.Add(self.selection_panel,1, wx.EXPAND)
        self.Add(data_selection_static_sizer, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, border=5)
        
        fit_type_static_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, 'Fit type'), wx.VERTICAL)
        
        self.fit_type = wx.Choice(self, wx.ID_ANY, choices=[ft.name for ft in fitting.get_fitting_tools()])
        fit_type_static_sizer.Add(self.fit_type,1, wx.ALIGN_RIGHT)
        self.Add(fit_type_static_sizer, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, border=5)
        
        fit_button = wx.Button(self, -1, "Fit")
        self.Add(fit_button, 0 , wx.ALIGN_CENTER_HORIZONTAL)
        wx.EVT_BUTTON(self, fit_button.GetId(), self.on_fit)
        wx.EVT_CHOICE(self, self.fit_type.GetId(), self.on_tool_choice)
        
        self.span = None
    
    
    def on_tool_choice(self, evnt):
        self.__current_tool_idx = self.fit_type.GetCurrentSelection()
    
            
    def on_fit(self, evnt):
        
        mask = self.selection_panel.get_selection()
        selected_idxs = numpy.where(mask)
        raw_x, raw_y = self.series.get_data()
        
        fitting_tool = fitting.get_fitting_tools()[self.__current_tool_idx]
        
        fit_x_data, fit_y_data, fit_params = fitting_tool.fit(raw_x[selected_idxs], 
                                                              raw_y[selected_idxs])
        
        FitDataSeries(self.series, fit_x_data, fit_y_data, fit_params)
        self.series.update()
    
    
    def on_control_panel_active(self):
        """
        This gets called automatically when the control panel is selected.
        """
        self.selection_panel.enable_selection()
    
    
    def on_control_panel_inactive(self):
        """
        This gets called automatically when the control panel is un-selected.
        """
        self.selection_panel.disable_selection()
        