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

class DataSeriesBase(object):
    def __init__(self, name):
        self.__name = name
        self.__plotted = False
    
    
    def plot(self, subplot):
        assert isinstance(subplot, AvoPlotSubplotBase), ('arg passed as '
                'subplot is not an AvoPlotSubplotBase instance')
        
        assert not self.__plotted, ('plot() should only be called once')
        
        self.__plotted = True
    
    
    def is_plotted(self):
        return self.__plotted
    
    def get_name(self):
        return self.__name
        


class XYDataSeries(DataSeriesBase):
    def __init__(self, name, xdata=None, ydata=None):
        super(XYDataSeries,self).__init__(name)
        self.set_xy_data(xdata, ydata)
        self._mpl_line = None
        
    @staticmethod    
    def get_supported_subplot_type():
        return AvoPlotXYSubplot
    
    
    def set_xy_data(self, xdata=None, ydata=None):
        self.__xdata = xdata
        self.__ydata = ydata
        
        if self.is_plotted():
            #update the the data in the plotted line
            self._mpl_line.set_data(*self.get_data())
    
    
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
        #TODO - preprocessing
        return (self.__xdata, self.__ydata)
    
    
    def plot(self, subplot):
        super(XYDataSeries,self).plot(subplot)
        
        self._mpl_line = subplot.get_mpl_axes().plot(*self.get_data())
        
        
        