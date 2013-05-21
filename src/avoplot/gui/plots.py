import wx
import os
import threading
import matplotlib
import datetime
import time

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure


def invalid_user_input(message):
        wx.MessageBox(message, "AvoPlot", wx.ICON_ERROR)



class PlotPanelBase(wx.ScrolledWindow):
    
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, wx.ID_ANY)
        self.SetScrollRate(2,2)
        self._is_panned = False
        self._is_zoomed = False
        self._gridlines = False
        
        self.parent = parent
        self.v_sizer = wx.BoxSizer(wx.VERTICAL)
        self.h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.h_sizer.Add(self.v_sizer, 1, wx.EXPAND)
        
        #the figure size is a bit arbitrary, but seems to work ok on my small screen - 
        #all this does is to set the minSize size hints for the sizer anyway.
        self.fig = Figure(figsize=(4,2))
        
        #set figure background to white
        #TODO - would this look better in default wx colour
        self.fig.set_facecolor((1,1,1))
        
        #try:
            #TODO - test this actually works on an up to date version of mpl
        #    matplotlib.pyplot.tight_layout()
        #except AttributeError:
            #probably an old version of mpl that does not have this function
        #    pass
        
        self.canvas = FigureCanvasWxAgg(self, -1, self.fig)
        
        self.tb = NavigationToolbar2Wx(self.canvas)
        self.tb.Show(False)
        
        self.v_sizer.Add(self.canvas, 1, wx.ALIGN_LEFT|wx.ALIGN_TOP|wx.EXPAND)

        self.SetSizer(self.h_sizer)
        self.h_sizer.Fit(self)
        self.SetAutoLayout(True)
                
        self.axes = self.fig.add_subplot(111)
    
    
    def close(self):
        #don't explicitly delete the window since it is managed by a notebook
        pass

        
    def set_status_bar(self, statbar):
        self.tb.set_status_bar(statbar)
    
    
    def go_home(self):
        self.axes.relim()
        self.axes.autoscale(enable=True)
        self.axes.autoscale_view()
        self.canvas.draw()
        self.canvas.gui_repaint()
 
    
    def zoom(self):
        self.tb.zoom()
        self._is_zoomed = not self._is_zoomed
        self._is_panned = False
    
    
    def pan(self):
        self.tb.pan()
        self._is_panned = not self._is_panned
        self._is_zoomed = False
    
    
    def gridlines(self, state):
        self.axes.grid(state)
        self._gridlines = state
        self.canvas.draw()
        self.canvas.gui_repaint()
    
    
    def save_plot(self):
        self.tb.save(None)
