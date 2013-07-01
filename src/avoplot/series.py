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
import matplotlib.colors
from avoplot.subplots import AvoPlotSubplotBase,AvoPlotXYSubplot
from avoplot import controls
from avoplot import core
import wx
class ColourSetting(wx.BoxSizer):
    def __init__(self, parent, label, default_colour, callback):
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)
        text = wx.StaticText(parent, -1, label)
        self.Add(text, 0, wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_LEFT)
        
        cp = wx.ColourPickerCtrl(parent, -1, default_colour)
        self.Add(cp, 0 , wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_LEFT)
        wx.EVT_COLOURPICKER_CHANGED(parent,cp.GetId(), callback)


class DataSeriesBase(core.AvoPlotElementBase):
    def __init__(self, name):
        super(DataSeriesBase,self).__init__(name)
        self.__plotted = False
        self._mpl_lines = []
        
    def set_parent_element(self, parent):
        assert isinstance(parent, AvoPlotSubplotBase) or parent is None
        super(DataSeriesBase,self).set_parent_element(parent)
    
    
    def get_mpl_lines(self):
        return self._mpl_lines
    
    
    def _plot(self, subplot):
        assert isinstance(subplot, AvoPlotSubplotBase), ('arg passed as '
                'subplot is not an AvoPlotSubplotBase instance')
        
        assert not self.__plotted, ('plot() should only be called once')
        
        self.__plotted = True
        
        self._mpl_lines = self.plot(subplot)
        self.setup_controls(subplot.get_parent_element())
    
    
    def plot(self, subplot):
        return []
    
    
    def preprocess(self, *args):
        return args
    
    
    def is_plotted(self):
        return self.__plotted   



class XYDataSeries(DataSeriesBase):
    def __init__(self, name, xdata=None, ydata=None):
        super(XYDataSeries,self).__init__(name)
        self.set_xy_data(xdata, ydata)
        self.add_control_panel(XYSeriesControls(self))
        
    @staticmethod    
    def get_supported_subplot_type():
        return AvoPlotXYSubplot
    
    
    def set_xy_data(self, xdata=None, ydata=None):
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
        xdata, ydata = super(XYDataSeries, self).preprocess(xdata, ydata)
        return xdata, ydata
        
    
    def plot(self, subplot):
        return subplot.get_mpl_axes().plot(*self.get_data())
        

class XYSeriesControls(controls.AvoPlotControlPanelBase):
    def __init__(self, series):
        super(XYSeriesControls, self).__init__("Series")
        self.series = series
        
               
    def setup(self, parent):
        super(XYSeriesControls, self).setup(parent)
        mpl_lines = self.series.get_mpl_lines()
        
        #add line colour controls
        line_col = matplotlib.colors.colorConverter.to_rgb(mpl_lines[0].get_color())
        print line_col
        line_col = (255 * line_col[0], 255 * line_col[1], 255 * line_col[2])
        cs = ColourSetting(self, "Line:", line_col, 
                           self.on_line_colour_change)
        self.Add(cs, 0 , wx.CENTER| wx.ALL, border=10)
        
    
    def on_line_colour_change(self, evnt):
        l, = self.series.get_mpl_lines()
        l.set_color(evnt.GetColour().GetAsString(wx.C2S_HTML_SYNTAX))
        l.axes.figure.canvas.draw()
        
        
    
    def on_suptitle_change(self, evnt):
        fig = self.figure.get_mpl_figure()
        if self.__suptitle_text is None:
            self.__suptitle_text = fig.suptitle(evnt.GetString())
        else:
            self.__suptitle_text.set_text(evnt.GetString())
        fig.canvas.draw()
                
        