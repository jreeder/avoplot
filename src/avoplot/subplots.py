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


class MetaCallMyInit(type):
    """
    Metaclass which ensures that a class's my_init() and setup_controls() 
    methods get called once, after it's __init__ method has returned.
    """
    def __call__(self, *args, **kw):
        obj=type.__call__(self, *args, **kw)
        obj.my_init()
        obj.setup_controls(obj.get_parent_element())
        return obj


class AvoPlotSubplotBase(core.AvoPlotElementBase):
    """
    The AvoPlotSubplotBase class is the base class for all subplots - which 
    represent a set of axes in the figure.
    """
    
    #metaclass ensures that my_init() is called once, after __init__ method
    #has completed. This requires a metaclass, because if the class is 
    #subclassed then there is a danger of my_init() being called multiple times
    #or being called before all the base class' __init__ methods have been 
    #called
    __metaclass__ = MetaCallMyInit
    
    def __init__(self, fig, name='subplot'):
        super(AvoPlotSubplotBase, self).__init__(name)
        self.set_parent_element(fig)
    
    
    def add_data_series(self, data):
        """
        Adds a data series to the subplot. data should be an instance of
        avoplot.series.DataSeriesBase or a subclass.
        """
        #assert isinstance(data, series.DataSeriesBase)
        data.set_parent_element(self)
        
        
    def set_parent_element(self, parent):
        """
        Overrides the AvoPlotElementBase class's method. Does the exactly
        the same as the base class but ensures that the parent is an 
        AvoPlotFigure instance.
        """
        assert isinstance(parent, AvoPlotFigure) or parent is None
        super(AvoPlotSubplotBase, self).set_parent_element(parent)
          
                     
    def my_init(self):
        """
        This method should be overridden by subclasses wishing to customise the
        look of the subplot before it is displayed.
        """
        pass
    
    
    def get_figure(self):
        """
        Returns the AvoPlotFigure instance that this subplot is contained 
        within. Use get_figure().get_mpl_figure() to get the matplotlib figure
        object that the subplot is associated with.
        """
        return self.get_parent_element()
    
    
    def on_mouse_button(self, evnt):
        """
        Event handler for mouse click events. These will be passed to the
        subplot from its parent figure. This should be overriden by subclasses.
        """
        pass
        
        
        

class AvoPlotXYSubplot(AvoPlotSubplotBase):
    """
    Subplot for containing 2D (XY) data series.
    """
    def __init__(self, fig, name='xy subplot'):
        super(AvoPlotXYSubplot, self).__init__(fig, name=name)
        
        #note the use of self.get_name() to ensure that the label is unique!
        self.__mpl_axes = fig.get_mpl_figure().add_subplot(111,
                                                           label=self.get_name())
        
        self.add_control_panel(XYSubplotControls(self))
        
    
    def delete(self):
        ax = self.get_mpl_axes()
        fig = self.get_parent_element()
        mpl_fig = fig.get_mpl_figure()
        
        mpl_fig.delaxes(ax)
        
        fig.update()
        
        super(AvoPlotXYSubplot, self).delete()
        
        
    
    def get_mpl_axes(self):
        """
        Returns the matplotlib axes object associated with this subplot.
        """
        return self.__mpl_axes  
    

    def on_mouse_button(self, evnt):
        """
        Event handler for mouse click events.
        """
        if evnt.inaxes != self.__mpl_axes: 
            return
        
        if evnt.button ==3:
            wx.CallAfter(self.on_right_click)
            #need to release the mouse otherwise everything hangs (under Linux at
            #least)
            self.get_figure().GetCapture().ReleaseMouse()
            return

      
    def on_right_click(self):
        """
        Called by on_mouse_button() if the event was a right-click. Creates
        a PopupMenu for adding new data series to the subplot.
        """
        menu = avoplot.gui.menu.get_subplot_right_click_menu(self)
        self.get_figure().PopupMenu(menu)
        menu.Destroy()
    
    
    def add_data_series(self, data):
        """
        Adds (i.e. plots) a data series into the subplot. data should be an
        avoplot.series.XYDataSeries instance or subclass thereof.
        """
        super(AvoPlotXYSubplot, self).add_data_series(data)
        data._plot(self)
        self.update()
        
    
    def update(self):
        """
        Redraws the subplot.
        """
        canvas = self.get_figure().canvas
        if canvas:
            canvas.draw()
        

class XYSubplotControls(controls.AvoPlotControlPanelBase):
    """
    Control panel for allowing the user to edit subplot parameters (title,
    axis labels etc.). The subplot argument should be an AvoPlotXYSubplot
    instance.
    """
    
    def __init__(self, subplot):
        super(XYSubplotControls, self).__init__("Subplot")
        self.subplot = subplot
    
    
    def setup(self, parent):
        """
        Creates all the controls for the panel.
        """
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
        """
        Event handler for the gridlines checkbox.
        """
        ax = self.subplot.get_mpl_axes()
        ax.grid(b=evnt.IsChecked())
        ax.figure.canvas.draw()
    
    
    def on_title(self, evnt):
        """
        Event handler for the subplot title text box.
        """
        ax = self.subplot.get_mpl_axes()
        ax.set_title(evnt.GetString())

        self.subplot.update()
        
        
    def on_xlabel(self, evnt):
        """
        Event handler for the x-axis title text box.
        """
        ax = self.subplot.get_mpl_axes()
        ax.set_xlabel(evnt.GetString())
        self.subplot.update()
    
    
    def on_ylabel(self, evnt):
        """
        Event handler for the y-axis title text box.
        """
        ax = self.subplot.get_mpl_axes()
        ax.set_ylabel(evnt.GetString())
        self.subplot.update()
    
    
    def on_bkgd_colour(self, evnt):
        """
        Event handler for the background colour selector.
        """
        ax = self.subplot.get_mpl_axes()
        ax.set_axis_bgcolor(evnt.GetColour().GetAsString(wx.C2S_HTML_SYNTAX))
        self.subplot.update()
            
    
        
        