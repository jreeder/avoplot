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

from avoplot.figure import AvoPlotFigure
import re
import avoplot.gui
import wx

#TODO - document this! ensures that my_init() is only called once, after
#all __init__ methods have finished
class MetaCallMyInit(type):
    def __call__(self, *args, **kw):
        obj=type.__call__(self, *args, **kw)
        obj.my_init()
        return obj


class AvoPlotSubplotBase(object):
    __metaclass__ = MetaCallMyInit
    def __init__(self, fig, name='subplot'):
        
        assert isinstance(fig, AvoPlotFigure)
        assert type(name) is str
        
        self._data_series = {}
        self.__name = None
        self.__figure = fig
        
        self.set_name(name)
    
            
    def my_init(self):
        pass
    
    
    def get_figure(self):
        return self.__figure
    
    
    def get_name(self):
        return self.__name
    
    
    def close(self):
        pass
    
    
    def on_mouse_button(self, evnt):
        pass
    
    
    def set_name(self, name):
        if name == self.__name:
            return
        
        if  self.__figure.subplots.has_key(name):
            existing_names = self.__figure.subplots.keys()
            current_indices = [1]
            for n in existing_names:
                if not n.startswith(name):
                    continue
                n = n[len(name):].strip()
                if n:
                        match = re.match(r'\(([0-9]+)\)', n)
                        if match:
                            current_indices.append(int(match.groups()[0]))
                                                
            name = ''.join([name, ' (%d)' % (max(current_indices) + 1)])
        
        self.__figure.subplots[name] = self
        
        if self.__name is not None:
            self.__figure.subplots.pop(self.__name)
        self.__name = name
        
        
        

class AvoPlotXYSubplot(AvoPlotSubplotBase):
    def __init__(self, fig, name='xy subplot'):
        super(AvoPlotXYSubplot, self).__init__(fig, name=name)
        
        #note the use of self.get_name() to ensure that the label is unique!
        self.__mpl_axes = fig.get_mpl_figure().add_subplot(111,label=self.get_name())
        
    
    def get_mpl_axes(self):
        return self.__mpl_axes  
    

    def on_mouse_button(self, evnt):
        if evnt.inaxes != self.__mpl_axes: 
            return
        
        if evnt.button ==3:
            wx.CallAfter(self.on_right_click)
            #need to release the mouse otherwise everything hangs (under Linux at
            #least)
            self.get_figure().ReleaseMouse()
            return

    
    
    def on_right_click(self):
        menu = avoplot.gui.menu.get_subplot_right_click_menu(self)
        self.get_figure().PopupMenu(menu)
        menu.Destroy()
    
    
    def add_data_series(self, series):
        self._data_series[series.get_name()] = series
        series.plot(self)
        canvas = self.get_figure().canvas
        if canvas:
            canvas.draw()
    
    