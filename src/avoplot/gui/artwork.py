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
import avoplot
import os.path




class AvoplotArtProvider(wx.ArtProvider):
    def __init__(self):
        wx.ArtProvider.__init__(self)

    def CreateBitmap(self, artid, client, size):
        
        if size.width == -1:
            sizerq = wx.ArtProvider.GetSizeHint(client)
            
            if sizerq.width == -1:
                sizerq = wx.Size(64,64)
        
        else:
            sizerq = size
        
        filename = os.path.join(avoplot.get_avoplot_icons_dir(),
                                '%dx%d'%(sizerq.width, sizerq.width), 
                                artid+'.png')

        return wx.Bitmap(filename,wx.BITMAP_TYPE_PNG)

