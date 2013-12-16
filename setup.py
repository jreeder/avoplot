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
This is the setup script for AvoPlot.

"""
import sys
import shutil
import os
import os.path
import stat
import string
import cPickle

from distutils.command.build import build
from distutils.command.install import install
from distutils.core import setup
from distutils.version import StrictVersion

#get the absolute path of this setup script
setup_script_path = os.path.dirname(os.path.abspath(sys.argv[0]))


####################################################################
#                    CONFIGURATION
####################################################################

required_modules = [("matplotlib", "the Matplotlib plotting library"),
                    ("numpy", "NumPy (Numerical Python)"),
                    ("wx", "wxPython"),
                   ]

data_files_to_install = []

#check that all the required modules are available
print "Checking for required Python modules..."
for mod, name in required_modules:
    try:
        print "importing %s..."%mod
        __import__(mod)
    except ImportError:
        print ("Failed to import \'%s\'. Please ensure that %s "
               "is correctly installed, then re-run this "
               "installer."%(mod,name))
        sys.exit(1)


## check that the required modules are all up-to-date enough ##
import matplotlib
if StrictVersion('1.0.1') > StrictVersion(matplotlib.__version__):
    print ("Your version of matplotlib is too old. AvoPlot requires >=1.0.1 "
           "but you have %s"%matplotlib.__version__)
    sys.exit()

import numpy
try:
    npy_vers = numpy.version.version
except:
    print ("Failed to determine what version of numpy you have installed."
           " Please ensure you have installed numpy >=1.4.0 and try again.")
    sys.exit() 

if StrictVersion('1.4.0') > StrictVersion(npy_vers):
    print ("Your version of numpy is too old. AvoPlot requires >=1.4.0 "
           "but you have %s"%npy_vers)
    sys.exit()
    
import wx
try:
    wx_vers = wx.version().split()[0]
except:
    print ("Failed to determine what version of wxPython you have installed."
           " Please ensure you have installed wxPython >=2.8.10 and try again.")
    sys.exit()

if wx_vers.count('.') > 2:
    wx_vers = '.'.join(wx_vers.split('.')[:3])
  
if StrictVersion('2.8.10') > StrictVersion(wx_vers):
    print ("Your version of wx is too old. AvoPlot requires >=2.8.10 "
           "but you have %s"%wx.version())
    sys.exit()


#platform specific configuration
scripts_to_install = [os.path.join('src','AvoPlot.py')]  

if sys.platform == "win32":
    #on windows we need to install the post-installation script too
    scripts_to_install.append(os.path.join('misc', 
                                           'avoplot_win32_postinstall.py'))
      


####################################################################
#                    BUILD/INSTALL
####################################################################
def ignore_hidden(src, names):
    """
    ignore function for use with shutil.copytree which causes hidden files to 
    be ignored
    """
    return [n for n in names if n.startswith('.')]



class CustomBuild(build):
    """
    Custom build command which copies the icons into the source tree before 
    continuing with the build.
    """
    def run(self):
        try:
            shutil.copytree('icons',os.path.join('src', 'avoplot', 'icons'), ignore=ignore_hidden)
            build.run(self)
            
        finally:
            shutil.rmtree(os.path.join('src', 'avoplot', 'icons'), False)



class RecordedInstall(install):
    def __init__(self,*args, **kwargs):
        install.__init__(self,*args, **kwargs)
        self.install_paths = {}
    
    
    def finalize_options (self):
        """
        Override the finalize_options method to record the install paths so that
        we can copy them into the build_info.py file during post-install
        """
        install.finalize_options(self)
        
        #note that these MUST be absolute paths
        self.install_paths['prefix'] = os.path.abspath(self.install_base)
        self.install_paths['install_data'] = os.path.abspath(self.install_data)
        self.install_paths['lib_dir'] = os.path.abspath(self.install_lib)
        self.install_paths['script_dir'] = os.path.abspath(self.install_scripts)
    
    
    def run_post_install_tasks(self):
        """
        Executes any tasks required after the installation is completed, e.g.
        creating .desktop files etc.
        """
        
        #create a desktop file (if we are in Linux)
        if sys.platform == "linux2":
            create_desktop_file(self.install_paths)
        
               
    def run(self):
        """
        Override the run function to also run post-install tasks.
        """
        install.run(self)
        self.execute(self.run_post_install_tasks, (), 
                     msg="Running post install tasks")
            
            
        
def create_desktop_file(install_paths):
    """
    Function to create the .desktop file for Linux installations.
    """
    import avoplot
    apps_folder = os.path.join(install_paths['prefix'],'share','applications')
    
    if not os.path.isdir(apps_folder):
        try:
            os.makedirs(apps_folder)
        except OSError:
            print ("Warning! Failed to create avoplot.desktop file. Unable to "
                   "create folder \'%s\'."%apps_folder)
            return
    
    desktop_file_path = os.path.join(apps_folder,'avoplot.desktop')
    
    with open(desktop_file_path,'w') as ofp:
        ofp.write('[Desktop Entry]\n')
        ofp.write('Version=%s\n'%avoplot.VERSION)
        ofp.write('Type=Application\n')
        ofp.write('Exec=%s\n'%os.path.join(install_paths['script_dir'],
                                           'AvoPlot.py'))
        ofp.write('Comment=%s\n'%avoplot.SHORT_DESCRIPTION)
        ofp.write('NoDisplay=false\n')
        ofp.write('Categories=Science;Education;\n')
        ofp.write('Name=%s\n'%avoplot.PROG_SHORT_NAME)
        ofp.write('Icon=%s\n'%os.path.join(avoplot.get_avoplot_icons_dir(),
                                           '64x64','avoplot.png'))
    
    return_code = os.system("chmod 644 " + os.path.join(apps_folder, 
                                                        'avoplot.desktop'))
    if return_code != 0:
        print ("Error! Failed to change permissions on \'" + 
               os.path.join(apps_folder, 'avoplot.desktop') + "\'")
                


#populate the list of data files to be installed
dirs = [d for d in os.listdir('icons') if os.path.isdir(os.path.join('icons',d))]
icon_files_to_install = []
for d in dirs:
    if d.startswith('.'):
        continue
    
    icon_files = os.listdir(os.path.join('icons',d))
    for f in icon_files:
        if f.startswith('.'):
            continue #skip the .svn folder
        icon_files_to_install.append(os.path.join('icons', d,f))
        

#if we're in Windows, then install the .ico file too
if sys.platform == "win32":
    icon_files_to_install.append(os.path.join('icons','avoplot.ico'))   


#now import the avoplot module to give us access to all the information
#about it, author name etc. 
import src.avoplot as avoplot_preinstall

#do the build/installation
setup(cmdclass={'install':RecordedInstall, 'build':CustomBuild}, #override the default installer 
      name=avoplot_preinstall.PROG_SHORT_NAME,
      version=avoplot_preinstall.VERSION,
      description=avoplot_preinstall.SHORT_DESCRIPTION,
      author=avoplot_preinstall.AUTHOR,
      author_email=avoplot_preinstall.AUTHOR_EMAIL,
      url=avoplot_preinstall.URL,
      package_dir={'':'src'},
      packages=['avoplot', 'avoplot.gui', 'avoplot.plugins', 
                'avoplot.plugins.avoplot_fromfile_plugin'],
      package_data={'avoplot':['COPYING'] + icon_files_to_install},
      scripts=scripts_to_install
      )
