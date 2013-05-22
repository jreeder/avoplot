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

import os
import os.path

import matplotlib
matplotlib.use('WXAgg')

__version__ = "0.0.1"

def get_avoplot_rw_dir():
    """
    Returns the path used by AvoScan for things like caching settings,
    storing templates etc. This is platform dependent, but on Linux it 
    will be in ~/.AvoScan
    """
    
    return os.path.join(os.path.expanduser('~'),".AvoPlot")


#make sure that all the directories that we are expecting to exist actually do.
try:
    os.makedirs(get_avoplot_rw_dir())
    
    #TODO - why is this sometimes created owned by root, with no rw permissions
except OSError:
    #dir already exists
    pass