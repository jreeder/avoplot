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

import matplotlib
matplotlib.use('WXAgg')

####################################################################
#                     Program Information
####################################################################
VERSION = "0.0"

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

#attempt to import the build_info module - this is dynamically generated at 
#install time and contains information about where the various files got 
#installed to.
try:
    import build_info

except ImportError:
    
    raise ImportError("Failed to import avoplot.build_info module. "
                      "There is a problem with your installation. Try "
                      "re-running the installer.")


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
    files, e.g. icons. On Linux at least this will probably be 
    something like /usr/local/share/AvoPlot
    """
    assert build_info.DATA_DIR is not None
    return os.path.join(build_info.DATA_DIR, PROG_SHORT_NAME)


def get_avoplot_icons_dir():
    """
    Returns the full path to the directory where the AvoPlot icons
    are stored.
    """
    return os.path.join(get_avoplot_sys_dir(),'icons')


#make sure that all the directories that we are expecting to exist actually do.
try:
    os.makedirs(get_avoplot_rw_dir())
    
    #TODO - why is this sometimes created owned by root, with no rw permissions
except OSError:
    #dir already exists
    pass
