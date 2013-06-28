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
from avoplot.subplots import AvoPlotSubplotBase,AvoPlotXYSubplot
from avoplot import controls
import wx

class DataSeriesBase(object):
    def __init__(self, name):
        self.__name = name
        self.__plotted = False
        self._mpl_lines = []
        
    
    def get_mpl_lines(self):
        return self._mpl_lines
    
    def _plot(self, subplot):
        assert isinstance(subplot, AvoPlotSubplotBase), ('arg passed as '
                'subplot is not an AvoPlotSubplotBase instance')
        
        assert not self.__plotted, ('plot() should only be called once')
        
        self.__plotted = True
        
        self._mpl_lines = self.plot(subplot)
    
    
    def plot(self, subplot):
        return []
    
    def preprocess(self, *args):
        return args
    
    def is_plotted(self):
        return self.__plotted
    
    
    def get_name(self):
        return self.__name     


class XYDataSeries(DataSeriesBase):
    def __init__(self, name, xdata=None, ydata=None):
        super(XYDataSeries,self).__init__(name)
        self.set_xy_data(xdata, ydata)
        
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
        

class TestCtrlPanel(controls.AvoPlotControlPanelBase):
    def __init__(self, data_series):
        super(TestCtrlPanel,self).__init__("Test")
        self.data_series = data_series
    
    def create(self, parent):
        super(TestCtrlPanel,self).create(parent)
        
        txt = wx.StaticText(parent, -1, "some text")
        self.Add(txt, 0)
                
        