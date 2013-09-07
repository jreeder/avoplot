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

import sys
required_modules = [("doas", "the Python DOAS library"),
                    ("avoplot", "AvoPlot"),
                    ("matplotlib", "the Matplotlib plotting library"),
                    ("numpy","NumPy (Numerical Python)"),
                    ("scipy","SciPy (scientific Python)"),
                    ("wx", "wxPython")
                   ]

#check that all the required modules are available
print "Checking for required Python modules..."
for mod,name in required_modules:
    try:
        print "importing "+mod+"..."
        __import__(mod)
    except ImportError:
        print "Failed to import \'"+mod+"\'. Please ensure that "+name+" is correctly installed, then re-run this installer."
        sys.exit(1)

print "Checking that we can monitor directories for changes..."
from doas import watcher
if not watcher.can_watch_directories():
    print "Error! No directory watching support is installed. For Linux, install pyinotify. For Windows, install the Python win32 API."
    sys.exit(1)

#there seems to be a problem with the "decimate" function in versions of scipy earlier
#than 0.9.0. Check the version here.
import scipy
version_as_int = lambda x: int("%02d%02d%02d"%tuple([int(i) for i in x.split('.')]))
if version_as_int(scipy.version.version) < version_as_int('0.9.0'):
    print "Error! The version of SciPy you have installed is too old. Please install version 0.9.0 or newer."
    sys.exit(1)

from avoplot.plugins import setup

setup(name='AvoPlot DOAS Plugin',
      version='0.0.1',
      description='AvoPlot plugin for analysing DOAS spectrum', 
      author = 'Nial Peters', 
      author_email='nonbiostudent@hotmail.com',
      package_dir = {'':'src'},
      packages=['avoplot_doas_plugin']
      )