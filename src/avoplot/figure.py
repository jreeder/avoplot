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
import matplotlib.colors
from avoplot import core
from avoplot import controls
from avoplot.gui import widgets
       

class FigureControls(controls.AvoPlotControlPanelBase):
    """
    Control panel for figure elements allowing the user to change the 
    background colour, title etc. of the figure.
    
    The figure argument must be an instance of AvoPlotFigure (or a subclass).
    """
    def __init__(self, figure):
        assert isinstance(figure, AvoPlotFigure), ('figure argument must be an '
                                                   'instance of AvoPlotFigure')
        super(FigureControls, self).__init__("Figure")
        self.figure = figure
        
           
    def setup(self, parent):
        """
        Creates all the figure editing controls.
        """
        super(FigureControls, self).setup(parent)
        mpl_fig = self.figure.get_mpl_figure()
        
        #TODO - if the figure already had a suptitle set, then this is going
        #to ignore it. Need a way to access the current suptitle text from the 
        #figure. My version of matplotlib doesn't seem to allow this.
        self.__suptitle_text = mpl_fig.suptitle('')
        
        #add figure title controls
        ts = widgets.TextSetting(self, "Title:", self.__suptitle_text)#self.on_suptitle_change)
        self.Add(ts, 0 , wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, border=10)
        
        #add background colour controls
        bkgd_col = mpl_fig.get_facecolor()
        bkgd_col = matplotlib.colors.colorConverter.to_rgb(bkgd_col)
        bkgd_col = (255 * bkgd_col[0], 255 * bkgd_col[1], 255 * bkgd_col[2])
        cs = widgets.ColourSetting(self, "Fill:", bkgd_col, 
                           self.on_bkgd_colour_change)
        self.Add(cs, 0 , wx.ALIGN_RIGHT| wx.LEFT | wx.RIGHT, border=10)
        


    def on_bkgd_colour_change(self, evnt):
        """
        Event handler for background colour selections.
        """
        fig = self.figure.get_mpl_figure()
        fig.set_facecolor(evnt.GetColour().GetAsString(wx.C2S_HTML_SYNTAX))
        
        self.figure.update()
        
    
    def on_suptitle_change(self, evnt):
        """
        Event handler for figure title changes.
        """
        self.__suptitle_text.set_text(evnt.GetString())
        
        self.figure.update()




class AvoPlotFigure(core.AvoPlotElementBase, wx.ScrolledWindow):
    """
    The AvoPlotFigure class represents a single plot tab in the plotting window.
    The parent argument should be the main (top-level) window.
    """
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
        
        #do the layout 
        self.SetSizer(self.v_sizer)
        self.v_sizer.Fit(self)
        self.SetAutoLayout(True)
    
    
    def enable_pan_and_zoom_tools(self, val):
        """
        If val == True, then enables the pan and zoom tools for the figure (in 
        fact for all open figures). If val == False, then disables them.
        """
        
        toolbar = self.parent.toolbar
        
        toolbar.set_pan_state(val)
        toolbar.set_zoom_state(val)
        
    
    def _destroy(self):
        """
        Overrides the base class method in order to call self.Destroy() to 
        free the figure window.
        """
        core.AvoPlotElementBase._destroy(self)
        self.Destroy()
    
    
    def update(self):
        """
        Redraws the entire figure.
        """
        if self.canvas is None:
            raise RuntimeError, "update() called before finalise()"
        
        self.canvas.draw()
    
    
    def is_zoomed(self):
        """
        Returns True if the zoom tool is selected, False otherwise.
        """
        return self._is_zoomed
    
    
    def is_panned(self):
        """
        Returns True if the pan tool is selected, False otherwise.
        """
        return self._is_panned
        
        
    def finalise(self, parent):
        """
        Creates the canvas for the figure to be drawn into. This is done here
        rather than in __init__ so that we have the option of vetoing the 
        displaying of the figure if something goes wrong during its 
        construction, e.g. if the file cannot be loaded etc.
        """
        
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
        """
        Returns the matplotlib figure object associated with this figure.
        """
        return self._mpl_figure
    
    
    def on_mouse_button(self,evnt):
        """
        Event handler for mouse click events in the figure canvas.
        """
        #if the zoom tools are active, then skip the event
        if self._is_panned or self._is_zoomed:
            return
        
        #otherwise find out what subplot it occurred in and pass the event over
        for subplot in self.get_child_elements():
            subplot.on_mouse_button(evnt)
        
        
    def set_status_bar(self, statbar):
        """
        Associates a status bar with this figure.
        """
        self.tb.set_status_bar(statbar)
    
    
    def set_subplot_layout_basic(self, positions):
        """
        Not yet implemented!
        positions = {name1:(row, col),name2:(row,col)}
        """
        raise NotImplementedError
    
    
    def go_home(self):
        """
        Returns all subplots within the figure to their default zoom level.
        """
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
        """
        Toggles the zoom functionality for the figure.
        """
        self._is_panned = False
        self._is_zoomed = not self._is_zoomed
        self.tb.zoom()
    
    
    def pan(self):
        """
        Toggles the pan/zoom functionality for the figure.
        """
        self._is_zoomed = False
        self._is_panned = not self._is_panned
        self.tb.pan()

    
    def save_figure_as_image(self):
        """
        Opens a file save dialog for exporting the figure to an image file - all
        matplotlib output formats are supported.
        """
        try:
            self.tb.save_figure(None)
        except NotImplementedError:
            self.tb.save(None)


