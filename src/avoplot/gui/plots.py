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
import matplotlib

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

import avoplot

def invalid_user_input(message):
        wx.MessageBox(message, avoplot.PROG_SHORT_NAME, wx.ICON_ERROR)



class PlotPanelBase(wx.ScrolledWindow):
    
    def __init__(self, parent, name):
        wx.ScrolledWindow.__init__(self, parent, wx.ID_ANY)
        self.SetScrollRate(2, 2)
        self._is_panned = False
        self._is_zoomed = False
        self._gridlines = False
        self.__data_follower = None
        self.name = name
        
        self.parent = parent
        self.v_sizer = wx.BoxSizer(wx.VERTICAL)
        self.h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.h_sizer.Add(self.v_sizer, 1, wx.EXPAND)
        
        #the figure size is a bit arbitrary, but seems to work ok on my small screen - 
        #all this does is to set the minSize size hints for the sizer anyway.
        self.fig = Figure(figsize=(4, 2))
        
        #set figure background to white
        #TODO - would this look better in default wx colour
        self.fig.set_facecolor((1, 1, 1))
        
        #try:
            #TODO - test this actually works on an up to date version of mpl
        #    matplotlib.pyplot.tight_layout()
        #except AttributeError:
            #probably an old version of mpl that does not have this function
        #    pass
        
        self.canvas = FigureCanvasWxAgg(self, -1, self.fig)
        
        self.tb = NavigationToolbar2Wx(self.canvas)
        self.tb.Show(False)
        
        self.v_sizer.Add(self.canvas, 1, wx.ALIGN_LEFT | wx.ALIGN_TOP | wx.EXPAND)

        self.SetSizer(self.h_sizer)
        self.h_sizer.Fit(self)
        self.SetAutoLayout(True)
                
        self.axes = self.fig.add_subplot(111)
        self.line = None
        
    
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
    
    
    def follow_data(self, state):
        if state:
            assert self.__data_follower is None
            self.__data_follower = DataFollower()
            self.__data_follower.connect(self.axes)
        else:
            self.__data_follower.disconnect()
            self.__data_follower = None
            
    
    def gridlines(self, state):
        self.axes.grid(state)
        self._gridlines = state
        self.canvas.draw()
        self.canvas.gui_repaint()
    
    
    def save_plot(self):
        self.tb.save(None)


class DataFollower:
    def __init__(self):
        self.line = None
    
    def connect(self, axes):
        self.axes = axes
        
        self.cid = self.axes.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)  
            
    def on_motion(self, event):
        if event.inaxes != self.axes: return
        if self.line is None:
            self.line, = self.axes.plot([event.xdata] * 2, self.axes.get_ylim(), 'k-')
            self.line.set_animated(True)
            
            
            trans = self.line.get_transform()
            inv_trans = trans.inverted()
            
            x0, y0 = inv_trans.transform_point([event.xdata - 10, self.axes.get_ylim()[1]])
            x1, y1 = inv_trans.transform_point([event.xdata + 10, self.axes.get_ylim()[0]])
            print "untransformed 0 = ", x0, y0
            print "untransformed 0 = ", x1, y1
            #add the line width to it
            #x0,y0 = trans.transform_point([x0-(self.line.get_linewidth()/2.0),y0])
            #x1,y1 = trans.transform_point([x1+(self.line.get_linewidth()/2.0),y1])
            
            #print "transformed 0 = ",x0,y0
            #print "transformed 0 = ",x1,y1
            bbox = matplotlib.transforms.Bbox([[x0, y0], [x1, y1]])
            #bbox.update_from_data_xy([[x0,y0],[x1,y1]])
            self.background = self.axes.figure.canvas.copy_from_bbox(self.line.axes.bbox)
            print self.background
            self.region_to_restore = bbox
            print bbox
            
            #print self.line.axes.bbox
            #print self.line.axes.bbox.bbox.update_from_data(numpy.array([[event.xdata-10, event.xdata+10],[event.xdata+10, self.axes.get_ylim()[1]]]))
            #print self.line.axes.bbox
        else:
            self.line.set_xdata([event.xdata] * 2,)
            self.line.set_ydata(self.line.axes.get_ylim())
            
#        x0, xpress, ypress = self.press
#        dx = event.xdata - xpress
#        dy = event.ydata - ypress
#
#        self.line.set_xdata([x0[0] + dx]*2)
#        self.line.set_ydata(self.line.axes.get_ylim())
#        self.line.set_linestyle('--')
#
        canvas = self.line.figure.canvas
        axes = self.line.axes
#        # restore the background region
        self.axes.figure.canvas.restore_region(self.background, bbox=self.region_to_restore)
#
#        # redraw just the current rectangle
        axes.draw_artist(self.line)
#
#        # blit just the redrawn area
        canvas.blit(self.axes.bbox)
        
        trans = self.line.get_transform()
        inv_trans = trans.inverted()
        
        x0, y0 = self.axes.transData.transform([event.xdata - 10, self.axes.get_ylim()[1]])
        x1, y1 = self.axes.transData.transform([event.xdata + 10, self.axes.get_ylim()[0]])
        print "untransformed 0 = ", x0, y0
        print "untransformed 0 = ", x1, y1
        #add the line width to it
        #x0,y0 = trans.transform_point([x0-(self.line.get_linewidth()/2.0),y0])
        #x1,y1 = trans.transform_point([x1+(self.line.get_linewidth()/2.0),y1])
        
        #print "transformed 0 = ",x0,y0
        #print "transformed 0 = ",x1,y1
        bbox = matplotlib.transforms.Bbox([[x0, y0], [x1, y1]])
        #bbox.update_from_data_xy([[x0,y0],[x1,y1]])
        self.region_to_restore = bbox

    
    def disconnect(self):
        self.axes.figure.canvas.mpl_disconnect(self.cid)
        self.axes.figure.canvas.restore_region(self.background)
        self.axes.figure.canvas.blit(self.axes.bbox)
        pass
