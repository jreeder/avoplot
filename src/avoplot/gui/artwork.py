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
import glob
import numpy


class AvoplotArtProvider(wx.ArtProvider):
    """
    Customised art provider class for serving the AvoPlot specific icons.
    """
    def __init__(self):
        wx.ArtProvider.__init__(self)
        
        #create a list of available icon sizes based on the names of the 
        #subfolders in the icons folder
        icon_dir = os.path.join(avoplot.get_avoplot_icons_dir(), '*x*')
        szs = [int(os.path.basename(f).split('x')[-1]) for f in glob.glob(icon_dir)]
        self.avail_sizes = numpy.array(szs)
        
            
    def _get_nearest_avail_size(self, s):
        """
        Returns the closest size to s that is available in the icons folder. If 
        no icons can be found, returns None
        """
        if not len(self.avail_sizes) > 0:
            return None
        
        return self.avail_sizes[numpy.argmin(numpy.abs(self.avail_sizes-s))]
    
    
    def CreateBitmap(self, artid, client, size):
        """
        Overrides CreateBitmap from wx.ArtProvider. This method looks in the 
        AvoPlot icons directory (as returned by avoplot.get_avoplot_icons_dir())
        for the icon specified by artid. The icons are split up into subfolders
        by size (for example "16x16") and this method will only look in the 
        relevant size subfolder for the requested icon.
        """
        if size.width == -1:
            sizerq = wx.ArtProvider.GetSizeHint(client)
            
            if sizerq.width == -1:
                sizerq = wx.Size(64,64)
        
        else:
            sizerq = size
        
        avail_size = self._get_nearest_avail_size(sizerq.width)
        if avail_size is None:
            return wx.NullBitmap
        
        filename = os.path.join(avoplot.get_avoplot_icons_dir(),
                                '%dx%d'%(avail_size, avail_size), 
                                artid+'.png')

        return wx.Bitmap(filename, wx.BITMAP_TYPE_PNG)

