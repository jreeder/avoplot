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

"""
This module is still under construction! Eventually, it will contain a set of
data analysis tools for working with data.
"""

#The DataFollower class is still under construction - come back soon!
#class DataFollower:
#    def __init__(self):
#        self.line = None
#    
#    def connect(self, axes):
#        self.axes = axes
#        
#        self.cid = self.axes.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)  
#            
#    def on_motion(self, event):
#        if event.inaxes != self.axes: return
#        if self.line is None:
#            self.line, = self.axes.plot([event.xdata] * 2, self.axes.get_ylim(), 'k-')
#            self.line.set_animated(True)
#            
#            
#            trans = self.line.get_transform()
#            inv_trans = trans.inverted()
#            
#            x0, y0 = inv_trans.transform_point([event.xdata - 10, self.axes.get_ylim()[1]])
#            x1, y1 = inv_trans.transform_point([event.xdata + 10, self.axes.get_ylim()[0]])
#            print "untransformed 0 = ", x0, y0
#            print "untransformed 0 = ", x1, y1
#            #add the line width to it
#            #x0,y0 = trans.transform_point([x0-(self.line.get_linewidth()/2.0),y0])
#            #x1,y1 = trans.transform_point([x1+(self.line.get_linewidth()/2.0),y1])
#            
#            #print "transformed 0 = ",x0,y0
#            #print "transformed 0 = ",x1,y1
#            bbox = matplotlib.transforms.Bbox([[x0, y0], [x1, y1]])
#            #bbox.update_from_data_xy([[x0,y0],[x1,y1]])
#            self.background = self.axes.figure.canvas.copy_from_bbox(self.line.axes.bbox)
#            print self.background
#            self.region_to_restore = bbox
#            print bbox
#            
#            #print self.line.axes.bbox
#            #print self.line.axes.bbox.bbox.update_from_data(numpy.array([[event.xdata-10, event.xdata+10],[event.xdata+10, self.axes.get_ylim()[1]]]))
#            #print self.line.axes.bbox
#        else:
#            self.line.set_xdata([event.xdata] * 2,)
#            self.line.set_ydata(self.line.axes.get_ylim())
#            
##        x0, xpress, ypress = self.press
##        dx = event.xdata - xpress
##        dy = event.ydata - ypress
##
##        self.line.set_xdata([x0[0] + dx]*2)
##        self.line.set_ydata(self.line.axes.get_ylim())
##        self.line.set_linestyle('--')
##
#        canvas = self.line.figure.canvas
#        axes = self.line.axes
##        # restore the background region
#        self.axes.figure.canvas.restore_region(self.background, bbox=self.region_to_restore)
##
##        # redraw just the current rectangle
#        axes.draw_artist(self.line)
##
##        # blit just the redrawn area
#        canvas.blit(self.axes.bbox)
#        
#        trans = self.line.get_transform()
#        inv_trans = trans.inverted()
#        
#        x0, y0 = self.axes.transData.transform([event.xdata - 10, self.axes.get_ylim()[1]])
#        x1, y1 = self.axes.transData.transform([event.xdata + 10, self.axes.get_ylim()[0]])
#        print "untransformed 0 = ", x0, y0
#        print "untransformed 0 = ", x1, y1
#        #add the line width to it
#        #x0,y0 = trans.transform_point([x0-(self.line.get_linewidth()/2.0),y0])
#        #x1,y1 = trans.transform_point([x1+(self.line.get_linewidth()/2.0),y1])
#        
#        #print "transformed 0 = ",x0,y0
#        #print "transformed 0 = ",x1,y1
#        bbox = matplotlib.transforms.Bbox([[x0, y0], [x1, y1]])
#        #bbox.update_from_data_xy([[x0,y0],[x1,y1]])
#        self.region_to_restore = bbox
#
#    
#    def disconnect(self):
#        self.axes.figure.canvas.mpl_disconnect(self.cid)
#        self.axes.figure.canvas.restore_region(self.background)
#        self.axes.figure.canvas.blit(self.axes.bbox)
#        pass