import os
import os.path

import matplotlib
matplotlib.use('WXAgg')

import avoscan

__version__ = "0.0.1"

#make sure that all the directories that we are expecting to exist actually do.
try:
    os.makedirs(os.path.join(avoscan.get_avoscan_rw_dir(),"AvoPlot"))
except OSError:
    #dir already exists
    pass