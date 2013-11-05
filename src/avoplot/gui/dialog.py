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
import sys

import avoplot

class AvoPlotDialog(wx.Dialog):
    """
    Base class for all Dialogs used in the GUI.
    """
    def __init__(self, parent, title):

        wx.Dialog.__init__(self, parent, wx.ID_ANY, title + " - " + 
                           avoplot.PROG_SHORT_NAME, style=wx.CLOSE_BOX | wx.CAPTION)
        
        #set up the icon for the frame
        if sys.platform == "win32":
            self.SetIcon(wx.ArtProvider.GetIcon("avoplot", size=(16, 16)))
        else:
            self.SetIcon(wx.ArtProvider.GetIcon("avoplot", size=(64, 64)))
            
            