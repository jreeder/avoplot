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

from matplotlib.patches import Rectangle
from matplotlib.transforms import blended_transform_factory
from matplotlib.colors import colorConverter
from matplotlib.pylab import date2num

from wx.lib.buttons import GenBitmapToggleButton as GenBitmapToggleButton
import wx
import numpy
import datetime

class DataRangeSelectionPanel(wx.Panel):
    
    def __init__(self, parent, series):
        """
        Panel to allow the user to select ranges of data from a plot.
        
            * parent - the parent wx.Window for the panel
            * series - the avoplot series that the selection is to be made from
        """
        self.series = series
        self.parent = parent
        
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        
        vsizer = wx.BoxSizer(wx.VERTICAL)
        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.all_select_button = GenBitmapToggleButton(self, wx.ID_ANY, wx.ArtProvider.GetBitmap("avoplot_allselect",wx.ART_BUTTON))
        self.h_select_button = GenBitmapToggleButton(self, wx.ID_ANY, wx.ArtProvider.GetBitmap("avoplot_hselect",wx.ART_BUTTON))
        self.v_select_button = GenBitmapToggleButton(self, wx.ID_ANY, wx.ArtProvider.GetBitmap("avoplot_vselect",wx.ART_BUTTON))
        self.rect_select_button = GenBitmapToggleButton(self, wx.ID_ANY, wx.ArtProvider.GetBitmap("avoplot_rectselect",wx.ART_BUTTON))
        
        self.all_select_button.SetToolTipString("Entire series")
        self.h_select_button.SetToolTipString("Horizontal selection")
        self.v_select_button.SetToolTipString("Vertical selection")
        self.rect_select_button.SetToolTipString("Rectangular selection")
        
        hsizer.AddSpacer(5)
        hsizer.Add(self.all_select_button, 0)
        hsizer.Add(self.h_select_button, 0, wx.LEFT, border=2)
        hsizer.Add(self.v_select_button, 0, wx.LEFT, border=2)
        hsizer.Add(self.rect_select_button, 0, wx.LEFT, border=2)
        hsizer.AddSpacer(5)
        
        wx.EVT_BUTTON(self, self.all_select_button.GetId(), self.on_allselect)
        wx.EVT_BUTTON(self, self.h_select_button.GetId(), self.on_hselect)
        wx.EVT_BUTTON(self, self.v_select_button.GetId(), self.on_vselect)
        wx.EVT_BUTTON(self, self.rect_select_button.GetId(), self.on_rectselect)
        
        
        self.all_select_button.SetValue(True)
        self.selection_tool = EntireSeriesSelectionTool(self.series)
        
        vsizer.AddSpacer(5)
        vsizer.Add(hsizer, 0, wx.ALIGN_CENTER_HORIZONTAL)
        
        self.SetSizer(vsizer)
        vsizer.Fit(self)
    
    
    
    def disable_selection(self):
        self.selection_tool.disable_selection()
    
    
    def enable_selection(self):
        self.selection_tool.enable_selection() 
        
    
    def __disable_all_except(self, button_to_keep):
        """
        De-selects all the selection buttons except the one passed as an arg.
        """
        self.selection_tool.disable_selection()
        
        for b in [self.all_select_button, self.h_select_button, 
                  self.v_select_button, self.rect_select_button]:
            
            if b != button_to_keep:
                b.SetValue(False)
    
    
    def get_selection(self):
        """
        Returns a numpy array which is a mask where 0 == data not selected and 
        1 == data selected. The length of the mask will be equal to that of the
        series.
        """
        return self.selection_tool.get_current_selection()
    
    
    def on_allselect(self, evnt):
        """
        Callback handler for the "select all" button.
        """
        self.__disable_all_except(self.all_select_button)
        self.selection_tool = EntireSeriesSelectionTool(self.series)
        self.selection_tool.enable_selection()
    
    
    def on_hselect(self, evnt):
        """
        Callback handler for the "horizontal select" button.
        """
        if not self.h_select_button.GetValue():
            self.all_select_button.SetValue(True)
            self.on_allselect(None)
            return
        
        self.__disable_all_except(self.h_select_button)
        self.selection_tool = HorizontalSelectionTool(self.series)
        self.selection_tool.enable_selection()
        
    
    def on_vselect(self, evnt):
        """
        Callback handler for the "vertical select" button.
        """
        if not self.v_select_button.GetValue():
            self.all_select_button.SetValue(True)
            self.on_allselect(None)
            return
        
        self.__disable_all_except(self.v_select_button)
        self.selection_tool = VerticalSelectionTool(self.series)
        self.selection_tool.enable_selection()
    
    
    def on_rectselect(self, evnt):
        """
        Callback handler for the "rectangular select" button.
        """
        if not self.rect_select_button.GetValue():
            self.all_select_button.SetValue(True)
            self.on_allselect(None)
            return
        
        self.__disable_all_except(self.rect_select_button)
        self.selection_tool = RectSelectionTool(self.series)
        self.selection_tool.enable_selection()   
        

def get_selection_box_colour(series):
    """
    Returns a colour (as an RGB tuple) that will be visible against the 
    background of the subplot.
    """  
    subplot = series.get_subplot()
    bkgd_col = colorConverter.to_rgb(subplot.get_mpl_axes().get_axis_bgcolor())
    
    return tuple([1.0 - c for c in bkgd_col])



class SelectionToolBase:
    def __init__(self, series):
        """
        Base class for selection tools. Must be subclassed.
        """
        self.series = series
    
    
    def disable_selection(self):
        """
        This must be implemented by the subclass - disables the selection tool
        and clears any current selection.
        """
        pass 
    
    def enable_selection(self):
        pass



class EntireSeriesSelectionTool(SelectionToolBase):
    """
    Tool for selecting the entire series.
    """
    def get_current_selection(self):
        return numpy.ones(len(self.series.get_raw_data()[0]))
    
    
class SpanSelector:

    def __init__(self, series, direction):
        """
        Selection tool that can select a number of horizontal or vertical strips
        of the data series. This class is based heavily on the 
        matplotlib.widgets.SpanSelector class.
        """
        self.series = series
        self.subplot = series.get_subplot()
        self.figure = self.subplot.get_figure()
        
        self.ax = self.subplot.get_mpl_axes()
        
        self.rect_colour = get_selection_box_colour(series)
        
        assert direction in ['horizontal', 'vertical', 'rectangular'], 'Must choose horizontal, vertical or rectangular for direction'
        self.direction = direction

        self.current_selection = []
        self.cids=[]

        self.rects = []
        self.cursor_hline = None
        self.cursor_vline = None
        self.background = None
        self.press_x = None
        self.press_y = None

        # Needed when dragging out of axes
        self.buttonDown = False
        self.prev = (0, 0)
        
        
        
    def enable_selection(self):
        self.visible = True
        
        #register the event handlers
        self.canvas = self.ax.figure.canvas
        self.cids.append(self.canvas.mpl_connect('motion_notify_event', self.on_move))
        self.cids.append(self.canvas.mpl_connect('button_press_event', self.on_click))
        self.cids.append(self.canvas.mpl_connect('button_release_event', self.on_release))
        self.cids.append(self.canvas.mpl_connect('draw_event', self.on_draw))
        
        #disable the pan and zoom controls
        self.subplot.get_figure().enable_pan_and_zoom_tools(False)
        
        #create the cursor line
        if self.direction in ('vertical', 'rectangular'):
            self.cursor_hline = self.ax.axhline(self.ax.get_ybound()[0], linewidth=1, color=self.rect_colour,
                                               animated=True)
            
        if self.direction in ('horizontal', 'rectangular'):
            self.cursor_vline = self.ax.axvline(self.ax.get_xbound()[0], linewidth=1, color=self.rect_colour,
                                               animated=True)
        

    def disable_selection(self):
        """
        Disables the selection tool - disconnecting the matplotlib canvas 
        callbacks and clearing any current selection.
        """
        for cid in self.cids:
                self.canvas.mpl_disconnect(cid)
        self.cids = []
        self.visible = False
        
        #remove the cursor lines from the subplot
        if self.cursor_hline is not None:
            self.cursor_hline.remove()
            self.cursor_hline = None
        
        if self.cursor_vline is not None:
            self.cursor_vline.remove()
            self.cursor_vline = None
        
        #remove any current selection
        self.clear_selection()
        
        #since the on_draw callback is now diasbled - need to clear the 
        #background cache
        self.background = None
        
  
    def on_draw(self, evnt):
        """
        Callback handler for draw events. Re-caches the background for future 
        blitting and redraws the selection rectangles.
        """
        self.update_background()
        self.update()
            
    
    def update_background(self):
        """
        Re-caches the backgound.
        """
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)


    def ignore(self, event):
        'Returns True if event should be ignored, false otherwise'
        return  (self.figure.is_zoomed() or
                 self.figure.is_panned() or
                 event.inaxes!=self.ax or 
                 not self.visible)


    def on_click(self, event):
        """
        Callback handler for mouse click events in the axis. Creates a new
        selection rectangle.
        """
        if self.ignore(event) or event.button !=1: 
            return
        
        self.buttonDown = True
        
        if not event.guiEvent.ControlDown() and self.current_selection:
            self.clear_selection()
        
        if self.background is None:
            self.update_background()
        
        self.press_x = event.xdata
        self.press_y = event.ydata
        
        if self.direction == 'horizontal':
            
            trans = blended_transform_factory(self.ax.transData, self.ax.transAxes)
            w,h = 0,1
                 
        elif self.direction == 'vertical':
            #vertical selection
            trans = blended_transform_factory(self.ax.transAxes, self.ax.transData)
            w,h = 1,0
        
        else:
            w,h, = 0,1
            trans = blended_transform_factory(self.ax.transData, self.ax.transData)
            
        self.rects.append(Rectangle((0,0), w, h,
                            transform=trans,
                            visible=False,
                            facecolor=self.rect_colour,
                            alpha=0.35,
                            animated=True
                            ))
        
        self.ax.add_patch(self.rects[-1])
            

    def clear_selection(self):
        """
        Clear the current selection
        """
        for r in self.rects:
            r.remove()
            
        self.rects = []
        self.update()
        
        self.current_selection = []
        
        
    def get_current_selection(self):
        """
        Returns a mask array where 1 == selected data point and 0 == not 
        selected data point. 
        """    
        xdata, ydata = self.series.get_data()
        selection_mask = numpy.zeros(len(xdata),dtype='int')
        
        #if xdata are datetimes, then need to convert them to numbers
        #first
        if len(xdata)>0 and type(xdata[0]) is datetime.datetime:
            xdata = numpy.array([date2num(d) for d in xdata])
        
        #if ydata are datetimes, then need to convert them to numbers
        #first
        if len(ydata)>0 and type(ydata[0]) is datetime.datetime:
            ydata = numpy.array([date2num(d) for d in ydata])
        
        if self.direction == 'rectangular':
            for xmin_sel, ymin_sel, xmax_sel, ymax_sel in self.current_selection:
                tmp_mask = numpy.where(numpy.logical_and(numpy.logical_and(xdata >= xmin_sel, 
                                                                           xdata <= xmax_sel),
                                                         numpy.logical_and(ydata >= ymin_sel,
                                                                           ydata <= ymax_sel)))

                selection_mask[tmp_mask] = 1
                
        elif self.direction == 'horizontal':
            for xmin_sel, ymin_sel, xmax_sel, ymax_sel in self.current_selection:
                tmp_mask = numpy.where(numpy.logical_and(xdata >= xmin_sel, 
                                                         xdata <= xmax_sel))
                selection_mask[tmp_mask] = 1
        
        else:
            for xmin_sel, ymin_sel, xmax_sel, ymax_sel in self.current_selection:
                tmp_mask = numpy.where(numpy.logical_and(ydata >= ymin_sel, 
                                                         ydata <= ymax_sel))
                selection_mask[tmp_mask] = 1
        
        return selection_mask
    
    
    def on_release(self, event):
        """
        Event handler for mouse click release events.
        """
        if self.press_x is None or (self.ignore(event) and not self.buttonDown) or event.button !=1:
            return
        
        self.buttonDown = False

        xmin = self.press_x
        ymin = self.press_y    
        xmax = event.xdata or self.prev[0]
        ymax = event.ydata or self.prev[1]

        xmin,xmax = sorted([xmin, xmax])
        ymin,ymax = sorted([ymin, ymax])
        
        self.current_selection.append((xmin, ymin, xmax, ymax))

        self.press_x = None
        self.press_y = None


    def update(self):
        """
        Redraws the selection rectangles.
        """
        if self.background is not None:
            self.canvas.restore_region(self.background)
        
        for r in self.rects:
            self.ax.draw_artist(r)
            
        if self.cursor_hline is not None:
            self.ax.draw_artist(self.cursor_hline)
        
        if self.cursor_vline is not None:
            self.ax.draw_artist(self.cursor_vline)
            
        self.canvas.blit(self.ax.bbox)


    def on_move(self, event):
        """
        Event handler for mouse move events.
        """
        if self.ignore(event):
            update_flag = False
            if self.cursor_hline is not None and self.cursor_hline.get_visible():
                self.cursor_hline.set_visible(False)
                update_flag = True
                
            if self.cursor_vline is not None and self.cursor_vline.get_visible():
                self.cursor_vline.set_visible(False)
                update_flag = True
                
            if update_flag:
                self.update()
            return
        
        if self.background is None:
            self.update_background()    
        
        x, y = event.xdata, event.ydata
        self.prev = x, y
        
        if self.cursor_hline is not None:
            self.cursor_hline.set_visible(True)
            self.cursor_hline.set_ydata([y,y])
            
        if self.cursor_vline is not None:
            self.cursor_vline.set_visible(True)
            self.cursor_vline.set_xdata([x,x])
        

        if self.press_x is None:
            #if the button is not pressed then nothing else to do
            self.update()
            return
        
        min_x, max_x = sorted([x,self.press_x])
        min_y, max_y = sorted([y, self.press_y])

        cur_rect = self.rects[-1]
        cur_rect.set_visible(True)
        
        if self.direction in ('horizontal', 'rectangular'):
            cur_rect.set_x(min_x)
            cur_rect.set_width(max_x-min_x)
            
        if self.direction in ('vertical', 'rectangular'):
            cur_rect.set_y(min_y)
            cur_rect.set_height(max_y-min_y)

        self.update()



class HorizontalSelectionTool(SpanSelector, SelectionToolBase):
    def __init__(self, series):
        """
        Tool for selecting horizontal sections of the data series.
        """
        SelectionToolBase.__init__(self, series)
        SpanSelector.__init__(self, series, 'horizontal')



class VerticalSelectionTool(SpanSelector, SelectionToolBase):
    def __init__(self, series):
        """
        Tool for selecting vertical sections of data series.
        """
        SelectionToolBase.__init__(self, series)
        SpanSelector.__init__(self, series, 'vertical')
        

class RectSelectionTool(SpanSelector, SelectionToolBase):
    def __init__(self, series):
        """
        Tool for selecting rectangular regions of data series.
        """        
        SelectionToolBase.__init__(self, series)
        SpanSelector.__init__(self, series, 'rectangular')