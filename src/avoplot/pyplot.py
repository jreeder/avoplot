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
from avoplot import series

class __PyplotXYDataSeries(series.XYDataSeries):
    def __init__(self, plot_args, plot_kwargs, xdata=None, ydata=None):
        self.__plot_args = plot_args #not including data
        self.__plot_kwargs = plot_kwargs
        
        fig_num = _get_current_fig_number()
        series.XYDataSeries(self, 'Figure %d'%fig_num, xdata=xdata, ydata=ydata)
    
    
    def plot(self, subplot):
        return subplot.get_mpl_axes().plot(*(self.get_data()+self.__plot_args), 
                                           **self.__plot_kwargs)



def _get_current_fig_number():
    pass


def plot(*args, **kwargs):
    #TODO - check how many series we need to create
    #need to check args for format strings (i.e. check the types)
    pass


def show():
    #add the series to the subplot
    #add the subplot to the figure
    #run any pending pyplot commands on the axes/series
    
    pass
