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
import matplotlib.colors
import re
import avoplot.gui
from avoplot.gui import widgets
from avoplot import core
from avoplot import controls
import wx

#TODO - document this! ensures that my_init() is only called once, after
#all __init__ methods have finished
class MetaCallMyInit(type):
    def __call__(self, *args, **kw):
        obj=type.__call__(self, *args, **kw)
        obj.my_init()
        obj.setup_controls(obj.get_parent_element())
        return obj


class AvoPlotSubplotBase(core.AvoPlotElementBase):
    __metaclass__ = MetaCallMyInit
    def __init__(self, fig, name='subplot'):
        super(AvoPlotSubplotBase, self).__init__(name)
        self.set_parent_element(fig)
    
    
    def add_data_series(self, data):
        #assert isinstance(data, series.DataSeriesBase)
        data.set_parent_element(self)
        
    
    def set_parent_element(self, parent):
        assert isinstance(parent, AvoPlotFigure) or parent is None
        super(AvoPlotSubplotBase, self).set_parent_element(parent)
          
                     
    def my_init(self):
        pass
    
    
    def get_figure(self):
        return self.get_parent_element()
    
    
    def close(self):
        pass
    
    
    def on_mouse_button(self, evnt):
        pass
        
        
        

class AvoPlotXYSubplot(AvoPlotSubplotBase):
    def __init__(self, fig, name='xy subplot'):
        super(AvoPlotXYSubplot, self).__init__(fig, name=name)
        
        #note the use of self.get_name() to ensure that the label is unique!
        self.__mpl_axes = fig.get_mpl_figure().add_subplot(111,label=self.get_name())
        
        self.add_control_panel(XYSubplotControls(self))
    
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
    
    
    def add_data_series(self, data):
        super(AvoPlotXYSubplot, self).add_data_series(data)
        data._plot(self)
        canvas = self.get_figure().canvas
        if canvas:
            canvas.draw()
        
    

class XYSubplotControls(controls.AvoPlotControlPanelBase):
    def __init__(self, subplot):
        super(XYSubplotControls, self).__init__("Subplot")
        self.subplot = subplot
    
    
    def setup(self, parent):
        super(XYSubplotControls, self).setup(parent)
        
        grid = wx.CheckBox(self, -1, "Gridlines")
        #TODO - if the axes already has a grid then this will ignore that
        self.Add(grid, 0, wx.ALIGN_LEFT|wx.ALL, border=10)
        wx.EVT_CHECKBOX(self, grid.GetId(), self.on_grid)
        
        ax = self.subplot.get_mpl_axes()
        bkgd_col = ax.get_axis_bgcolor()
        bkgd_col = matplotlib.colors.colorConverter.to_rgb(bkgd_col)
        bkgd_col = (255 * bkgd_col[0], 255 * bkgd_col[1], 255 * bkgd_col[2])
        colour = widgets.ColourSetting(self, 'Background', bkgd_col,
                                       self.on_bkgd_colour)
        self.Add(colour, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, border=10) 
        
        title = widgets.TextSetting(self, 'Subplot title:', ax.get_title(), 
                                     self.on_title)  
        self.Add(title, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, border=10) 
        
        xlabel = widgets.TextSetting(self, 'x-axis title:', ax.get_xlabel(), 
                                     self.on_xlabel)        
        self.Add(xlabel, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, border=10)
        
        ylabel = widgets.TextSetting(self, 'y-axis title:', ax.get_ylabel(), 
                                     self.on_ylabel)        
        self.Add(ylabel, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, border=10)
    
    
    def on_grid(self, evnt):
        ax = self.subplot.get_mpl_axes()
        ax.grid(b=evnt.IsChecked())
        ax.figure.canvas.draw()
    
    def on_title(self, evnt):
        ax = self.subplot.get_mpl_axes()
        ax.set_title(evnt.GetString())
        ax.figure.canvas.draw()
        
    def on_xlabel(self, evnt):
        ax = self.subplot.get_mpl_axes()
        ax.set_xlabel(evnt.GetString())
        ax.figure.canvas.draw()
    
    def on_ylabel(self, evnt):
        ax = self.subplot.get_mpl_axes()
        ax.set_ylabel(evnt.GetString())
        ax.figure.canvas.draw()
    
    def on_bkgd_colour(self, evnt):
        ax = self.subplot.get_mpl_axes()
        ax.set_axis_bgcolor(evnt.GetColour().GetAsString(wx.C2S_HTML_SYNTAX))
        ax.figure.canvas.draw()
            
    
        
        