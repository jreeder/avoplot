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
import warnings
import sys
import collections

import matplotlib
matplotlib.use('WXAgg')

####################################################################
#                     Program Information
####################################################################
VERSION = "14.01" #year.month of release

AUTHOR = 'Nial Peters'

AUTHOR_EMAIL = 'nonbiostudent@hotmail.com'

URL = 'http://code.google.com/p/avoplot/'

PROG_SHORT_NAME = 'AvoPlot'

PROG_LONG_NAME = 'AvoPlot'

SHORT_DESCRIPTION = 'Plot scientific data'

LONG_DESCRIPTION = ''

COPYRIGHT = 'Copyright (C) Nial Peters 2013'

COPY_PERMISSION =(
'\n%s is free software: you can redistribute it and/or modify\n'
'it under the terms of the GNU General Public License as published by\n'
'the Free Software Foundation, either version 3 of the License, or\n'
'(at your option) any later version.\n'
'\n'
'%s is distributed in the hope that it will be useful,\n'
'but WITHOUT ANY WARRANTY; without even the implied warranty of\n'
'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n'
'GNU General Public License for more details.\n'
'\n'
'You should have received a copy of the GNU General Public License\n'
'along with %s.  If not, see <http://www.gnu.org/licenses/>.\n'
''%(PROG_SHORT_NAME, PROG_SHORT_NAME, PROG_SHORT_NAME))

SRC_FILE_HEADER = ('#%s\n\nThis file is part of %s.\n\n%s'
                   ''%(COPYRIGHT, PROG_SHORT_NAME, 
                       COPY_PERMISSION)).replace('\n','\n#')

####################################################################

def get_avoplot_rw_dir():
    """
    Returns the path used by AvoPlot for things like caching settings,
    storing templates etc. This is platform dependent, but on Linux it 
    will be in ~/.AvoPlot
    """
    
    if sys.platform == 'win32':
        #Windows doesn't really do hidden directories, so get rid of the dot
        return os.path.join(os.path.expanduser('~'),"%s"%PROG_SHORT_NAME)
    else:
        return os.path.join(os.path.expanduser('~'),".%s"%PROG_SHORT_NAME)


def get_avoplot_sys_dir():
    """
    Returns the path used by AvoPlot to store user independent 
    files
    """
    return __path__[0]


def get_avoplot_icons_dir():
    """
    Returns the full path to the directory where the AvoPlot icons
    are stored.
    """
    return os.path.join(get_avoplot_sys_dir(),'icons')


def get_license_file():
    """
    Returns the full path to the COPYING file installed with AvoPlot
    """
    return os.path.join(__path__[0],'COPYING')


def call_on_idle(func, *args, **kwargs):
    """
    Registers a callable to be executed when the event loop is empty. The
    callable will only be called once. This is used to execute the _destroy()
    method of AvoPlotElementBase. 
    """
    call_on_idle.idle_q.append((func, args, kwargs))

call_on_idle.idle_q = collections.deque()


#make sure that all the directories that we are expecting to exist actually do.
try:
    os.makedirs(get_avoplot_rw_dir())
    
except OSError:
    #dir already exists
    pass
