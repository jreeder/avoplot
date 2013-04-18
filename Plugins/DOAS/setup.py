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
if scipy.version.version < '0.9.0':
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