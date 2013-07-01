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

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

from avoplot import core
from avoplot import controls


class ColourSetting(wx.BoxSizer):
    def __init__(self, parent, label, default_colour, callback):
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)
        text = wx.StaticText(parent, -1, label)
        self.Add(text, 0, wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_LEFT)
        
        cp = wx.ColourPickerCtrl(parent, -1, default_colour)
        self.Add(cp, 0 , wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_LEFT)
        wx.EVT_COLOURPICKER_CHANGED(parent,cp.GetId(), callback)


class TextSetting(wx.BoxSizer):
    def __init__(self, parent, label, default_text, callback):
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)
        text = wx.StaticText(parent, -1, label)
        self.Add(text, 0, wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_LEFT)
        
        self.tc = wx.TextCtrl(parent, -1, value=default_text, 
                              style=wx.TE_PROCESS_ENTER)
        wx.EVT_TEXT(parent, self.tc.GetId(), callback)
        self.Add(self.tc, 0, wx.EXPAND)
        
        
        

class FigureControls(controls.AvoPlotControlPanelBase):
    def __init__(self, figure):
        super(FigureControls, self).__init__("Figure")
        self.figure = figure
        
           
    def setup(self, parent):
        super(FigureControls, self).setup(parent)
        mpl_fig = self.figure.get_mpl_figure()
        
        self.__suptitle_text = None
        
        #add background colour controls
        bkgd_col = mpl_fig.get_facecolor()
        bkgd_col = (255 * bkgd_col[0], 255 * bkgd_col[1], 255 * bkgd_col[2])
        cs = ColourSetting(self, "Background:", bkgd_col, 
                           self.on_bkgd_colour_change)
        self.Add(cs, 0 , wx.CENTER| wx.ALL, border=10)
        
        #add figure title controls
        if mpl_fig._suptitle is not None:
            title = mpl_fig._suptitle.get_text()
        else:
            title = ""
        
        ts = TextSetting(self, "Title:", title, self.on_suptitle_change)
        self.Add(ts, 0 , wx.CENTER| wx.ALL, border=10)
        
    
    
    def on_bkgd_colour_change(self, evnt):
        fig = self.figure.get_mpl_figure()
        fig.set_facecolor(evnt.GetColour().GetAsString(wx.C2S_HTML_SYNTAX))
        fig.canvas.draw()
        
    
    def on_suptitle_change(self, evnt):
        fig = self.figure.get_mpl_figure()
        if self.__suptitle_text is None:
            self.__suptitle_text = fig.suptitle(evnt.GetString())
        else:
            self.__suptitle_text.set_text(evnt.GetString())
        fig.canvas.draw()




class AvoPlotFigure(core.AvoPlotElementBase, wx.ScrolledWindow):
    
    def __init__(self, parent, name):
        core.AvoPlotElementBase.__init__(self, name)       
        self.parent = parent
        self.canvas = None
        
        self._is_zoomed = False
        self._is_panned = False

        #set up the scroll bars in case the figure gets too small
        wx.ScrolledWindow.__init__(self, parent, wx.ID_ANY)
        self.SetScrollRate(2, 2)
        self.v_sizer = wx.BoxSizer(wx.VERTICAL)
        

        
        #the figure size is a bit arbitrary, but seems to work ok on my small 
        #screen - all this does is to set the minSize size hints for the 
        #sizer anyway.
        #TODO - this may cause problems when it comes to printing/saving the
        #figure.
        self._mpl_figure = Figure(figsize=(4, 2))
        
        #set figure background to white
        self._mpl_figure.set_facecolor((1, 1, 1))
        
        self.add_control_panel(FigureControls(self))
        self.setup_controls(self)
        
        #do the layout 
        self.SetSizer(self.v_sizer)
        self.v_sizer.Fit(self)
        self.SetAutoLayout(True)
    
    
    def finalise(self):
        #embed the figure in a wx canvas, ready to be put into the main window
        self.canvas = FigureCanvasWxAgg(self, -1, self._mpl_figure)
        self.cid = self.canvas.mpl_connect('button_press_event', 
                                           self.on_mouse_button)
        
        #create, but don't display the matplotlib navigation toolbar. This
        #does all the hard work of setting up the zoom/pan functionality
        self.tb = NavigationToolbar2Wx(self.canvas)
        self.tb.Show(False)
        self.v_sizer.Add(self.canvas, 1, 
                         wx.ALIGN_LEFT | wx.ALIGN_TOP | wx.EXPAND)
        
    
    
    def get_mpl_figure(self):
        return self._mpl_figure
    
    
    def on_mouse_button(self,evnt):
        #if the zoom tools are active, then skip the event
        if self._is_panned or self._is_zoomed:
            return
        
        #otherwise find out what subplot it occurred in and pass the event over
        for subplot in self.get_child_elements():
            subplot.on_mouse_button(evnt)
        
    
    
    def close(self):
        #don't explicitly delete the window since it is managed by a notebook
        #but need to close each subplot held by the figure in case the subplot
        #is executing some background task that needs to be stopped (e.g. a
        #realtime plotting thread)
        for s_name in self.subplots.keys():
            self.subplots[s_name].close()
            
            #also remove the subplot from the figure, in case someone tries
            #to reuse the figure object for some reason
            self.subplots.pop(s_name)

        
    def set_status_bar(self, statbar):
        self.tb.set_status_bar(statbar)
    
    
    def set_subplot_layout_basic(self, positions):
        """
        positions = {name1:(row, col),name2:(row,col)}
        """
        raise NotImplementedError
    
    
    def go_home(self):
        #return all the subplots to their default (home) zoom level
        for s in self.get_child_elements():
            ax = s.get_mpl_axes()
            ax.relim()
            ax.autoscale(enable=True)
            ax.autoscale_view()
        
        #show the changes    
        self.canvas.draw()
        self.canvas.gui_repaint()
 
    
    def zoom(self):
        self._is_panned = False
        self._is_zoomed = not self._is_zoomed
        self.tb.zoom()
    
    
    def pan(self):
        self._is_zoomed = False
        self._is_panned = not self._is_panned
        self.tb.pan()

    
    
    def save_figure_as_image(self):
        self.tb.save_figure(None)


