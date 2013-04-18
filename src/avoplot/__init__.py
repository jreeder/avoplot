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