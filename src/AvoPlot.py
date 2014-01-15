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
This module contains the main script for running AvoPlot.
"""

import optparse

import avoplot
from avoplot.gui import  main

def __parse_cmd_line():
    """
    Function parses the command line input and returns a tuple 
    of (options, args).
    """
    usage = ("Usage: %prog [options]")
        
    parser = optparse.OptionParser(usage, version=avoplot.VERSION)

    (options, args) = parser.parse_args()

    return (options, args)


if __name__ == '__main__':
    
    #parse any command line args
    options, args = __parse_cmd_line()
    
    #create and run the wx app    
    app = main.AvoPlotApp(options, args)
    app.MainLoop()

    
