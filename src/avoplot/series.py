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
import matplotlib.colors

from avoplot.subplots import AvoPlotSubplotBase, AvoPlotXYSubplot
from avoplot import controls
from avoplot import core
from avoplot.gui import widgets


class DataSeriesBase(core.AvoPlotElementBase):
    """
    Base class for all data series.
    """
    
    def __init__(self, name):
        super(DataSeriesBase, self).__init__(name)
        self.__plotted = False
        self._mpl_lines = []
        
        
    def set_parent_element(self, parent):
        """
        Overrides AvoPlotElementBase method. Does exactly the same, but ensures 
        that parent is an instance of AvoPlotSubplotBase or a subclass thereof.
        """
        assert isinstance(parent, AvoPlotSubplotBase) or parent is None
        super(DataSeriesBase, self).set_parent_element(parent)
    
    
    def get_mpl_lines(self):
        """
        Returns a list of matplotlib line objects associated with the data 
        series.
        """
        assert self.__plotted, ('Data series must be plotted before you can '
                                'access the matplotlib lines')
        return self._mpl_lines
    
    
    def delete(self):

        self._mpl_lines.pop(0).remove()
        self.update()
        super(DataSeriesBase, self).delete()        
        
        
    def _plot(self, subplot):
        """
        Called in subplot.add_data_series() to plot the data into the subplot
        and setup the controls for the series (the parent of the series is not
        known until it gets added to the subplot)
        """
        assert isinstance(subplot, AvoPlotSubplotBase), ('arg passed as '
                'subplot is not an AvoPlotSubplotBase instance')
        
        assert not self.__plotted, ('plot() should only be called once')
        
        self.__plotted = True
        
        self._mpl_lines = self.plot(subplot)
        self.setup_controls(subplot.get_parent_element())
    
    
    def update(self):
        """
        Redraws the series.
        """
        parent = self.get_parent_element()
        if parent: #parent could be None - in which case do nothing
            parent.update()
    
    
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
        
        
    @staticmethod    
    def get_supported_subplot_type():
        """
        Static method that returns the class of subplot that the data series
        can be plotted into. This will be a subclass of AvoPlotSubplotBase.
        """
        return AvoPlotXYSubplot
    
    
    def set_xy_data(self, xdata=None, ydata=None):
        """
        Sets the x and y values of the data series.
        """
        self.__xdata = xdata
        self.__ydata = ydata
        
        if self.is_plotted():
            #update the the data in the plotted line
            line, = self.get_mpl_lines()
            line.set_data(*self.get_data())
    
    
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
        return self.preprocess(self.__xdata, self.__ydata)
    
    
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
        
        #add line controls
        linestyle = widgets.ChoiceSetting(self, 'Line:', mpl_lines[0].get_linestyle(),
                                       ['None', '-', '--', '-.', ':'], self.on_linestyle)
        
        line_col = matplotlib.colors.colorConverter.to_rgb(mpl_lines[0].get_color())
        line_col = (255 * line_col[0], 255 * line_col[1], 255 * line_col[2])
        cs = widgets.ColourSetting(self, "", line_col,
                           self.on_line_colour_change)
        linestyle.Add(cs, 0 , wx.ALIGN_LEFT | wx.ALL, border=10)
        self.Add(linestyle, 0 , wx.ALIGN_LEFT | wx.ALL, border=10)
        
        
        marker = widgets.ChoiceSetting(self, 'Marker:', mpl_lines[0].get_marker(),
                                       ['None', '.', '+', 'x'], self.on_marker)
        
        prev_col = matplotlib.colors.colorConverter.to_rgb(mpl_lines[0].get_markeredgecolor())
        
        #explicitly set the the marker colour to its existing value, otherwise
        #it will get changed if we change the line colour
        mpl_lines[0].set_markeredgecolor(mpl_lines[0].get_markeredgecolor())
        mpl_lines[0].set_markerfacecolor(mpl_lines[0].get_markerfacecolor())
        
        prev_col = (255 * prev_col[0], 255 * prev_col[1], 255 * prev_col[2])
        marker_col = widgets.ColourSetting(self, "", prev_col,
                                           self.on_marker_colour)
        
        marker.Add(marker_col, wx.ALIGN_LEFT | wx.ALL, border=10)
        self.Add(marker, 0 , wx.ALIGN_LEFT | wx.ALL, border=10)
    
    
    def on_marker_colour(self, evnt):
        """
        Event handler for marker colour change events
        """
        l, = self.series.get_mpl_lines()
        l.set_markeredgecolor(evnt.GetColour().GetAsString(wx.C2S_HTML_SYNTAX))
        l.set_markerfacecolor(evnt.GetColour().GetAsString(wx.C2S_HTML_SYNTAX))
        self.series.update()
    
    
    def on_marker(self, evnt):
        """
        Event handler for marker style change events.
        """
        l, = self.series.get_mpl_lines()
        l.set_marker(evnt.GetString())
        self.series.update()
    
    
    def on_line_colour_change(self, evnt):
        """
        Event handler for line colour change events.
        """
        l, = self.series.get_mpl_lines()
        l.set_color(evnt.GetColour().GetAsString(wx.C2S_HTML_SYNTAX))
        self.series.update()
        
    
    def on_linestyle(self, evnt):
        """
        Event handler for line style change events.
        """
        l, = self.series.get_mpl_lines()
        l.set_linestyle(evnt.GetString())
        self.series.update()
    
                
        
