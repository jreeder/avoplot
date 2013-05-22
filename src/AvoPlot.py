#!/usr/bin/python

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
This module contains the main script for running AvoPlot. It doesn't really do
very much except to launch the GUI.
"""

import wx

from avoplot.gui import main
import avoplot.plugins


if __name__ == '__main__':
        
    app = wx.PySimpleApp()
    avoplot.plugins.load_all_plugins()
    main.MainFrame()
       
    app.MainLoop()
