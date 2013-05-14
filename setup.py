from distutils.core import setup
import sys
import shutil
import os
import stat


required_modules = [("matplotlib", "the Matplotlib plotting library"),
                    ("numpy","NumPy (Numerical Python)"),
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

if sys.platform == "linux2":
    apps_folder = '/usr/share/applications'
    icon_folder = '/usr/share/icons'
    desktop_folder = os.path.expandvars("$HOME/Desktop")
    
    avoplot_files_to_install = [(icon_folder,['icons/avoplot.png']),
                                (apps_folder,['misc/avoplot.desktop'])]
    
    avoplot_scripts_to_install = [os.path.normpath('src/AvoPlot.py')]    
       
elif sys.platform == "win32":
    avoplot_files_to_install = [("icons",[os.path.join('icons','avoplot.ico')])]
    avoplot_scripts_to_install = [os.path.join('src','AvoPlot.py'),os.path.join('misc','avoscan_win32_postinstall.py')]

else:
    raise RunTimeError, "Unsupported platform"


setup(name='AvoPlot',
      version='0.0.1',
      description='Plotting program for visualising DOAS data', 
      author = 'Nial Peters', 
      author_email='nonbiostudent@hotmail.com',
      package_dir = {'':'src'},
      packages=['avoplot','avoplot.gui', 'avoplot.plugins', 'avoplot.plugins.avoplot_fromfile_plugin'],
      scripts=avoplot_scripts_to_install,
      data_files=avoplot_files_to_install 
      )



#post install
if sys.argv.count('install') != 0:
    if sys.platform == "linux2":
        #make sure the .desktop file on the apps directory has the correct permissions
        return_code = os.system("chmod 644 "+os.path.join(apps_folder, 'avoplot.desktop'))
        if return_code != 0:
                print "Error! Failed to change execute permissions on \'"+os.path.join(apps_folder, 'avoplot.desktop')+"\'"
        
        #make sure the icon file is readable
        return_code = os.system("chmod 644 "+os.path.join(icon_folder, 'avoplot.png'))
        if return_code != 0:
                print "Error! Failed to change execute permissions on \'"+os.path.join(icon_folder, 'avoplot.png')+"\'"
        