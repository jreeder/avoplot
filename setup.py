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

It is a little more complex than a "standard" distutils setup script because
it also creates the build_info.py module in AvoPlot. This contains information
about how the program gets installed, which is then used by AvoPlot to determine
things like where its icons files are etc. In order to get access to this 
information at install time, we have overridden the standard distutils install
class with one which creates the build_info.py file once installation options 
have been finalised.
"""
import sys
import shutil
import os
import stat
import string

from distutils.command.build_py import build_py as _build_py
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
install_paths = {}

class RecordedInstall(install):
    
    def finalize_options (self):
        """
        Override the finalize_options method to record the install paths so that
        we can copy them into the build_info.py file during post-install
        """
        install.finalize_options(self)
        install_paths['prefix'] = self.install_base
        install_paths['install_data'] = self.install_data
        install_paths['lib_dir'] = self.install_lib
        install_paths['script_dir'] = self.install_scripts



def create_desktop_file():
    """
    Function to create the .desktop file for Linux installations.
    """
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
        ofp.write('Exec=%s\n'%os.path.join(avoplot.build_info.SCRIPT_DIR,
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
if sys.platform == "linux2":
    data_prefix = 'share/AvoPlot'
else:
    data_prefix = 'AvoPlot'

dirs = [d for d in os.listdir('icons') if os.path.isdir(os.path.join('icons',d))]
for d in dirs:
    if d.startswith('.'):
        continue
    
    icon_files = os.listdir(os.path.join('icons',d))
    files = []
    for f in icon_files:
        if f.startswith('.'):
            continue #skip the .svn folder
        files.append(os.path.join('icons', d,f))
        
    data_files_to_install.append((os.path.join(data_prefix, 'icons', d),files))


#if we're in Windows, then install the .ico file too
if sys.platform == "win32":
    data_files_to_install.append((os.path.join(data_prefix, 'icons'),
                                  [os.path.join('icons','avoplot.ico')]))    


try:
    #create a temporary build_info module - this will be populated during the 
    #build process. Note that we define DATA_DIR in the file so that we can 
    #import avoplot without errors.
    build_info_name = os.path.join(setup_script_path, 'src', 'avoplot', 
                                   'build_info.py')
    with open(build_info_name, 'w') as ofp:
        ofp.write("#Temporary file created by setup.py. It should be deleted "
                  "again when setup.py exits.\n\n"
                  "DATA_DIR = None\n")
    
    #now import the avoplot module to give us access to all the information
    #about it, author name etc. This must be done after the temp build_info
    #file is created, otherwise the import will fail
    import src.avoplot as avoplot_preinstall
    
    #do the build/installation
    setup(cmdclass={'install':RecordedInstall}, #override the default installer 
          name=avoplot_preinstall.PROG_SHORT_NAME,
          version=avoplot_preinstall.VERSION,
          description=avoplot_preinstall.SHORT_DESCRIPTION,
          author=avoplot_preinstall.AUTHOR,
          author_email=avoplot_preinstall.AUTHOR_EMAIL,
          url=avoplot_preinstall.URL,
          package_dir={'':'src'},
          packages=['avoplot', 'avoplot.gui', 'avoplot.plugins', 
                    'avoplot.plugins.avoplot_fromfile_plugin'],
          package_data={'avoplot':['COPYING']},
          data_files=data_files_to_install,
          scripts=scripts_to_install
          )

    
####################################################################
#                    POST INSTALL
####################################################################
    import avoplot #imported from its installed location
    
    if sys.argv.count('install') != 0:
        #populate the build_info file
        installed_build_info_filename = os.path.splitext(avoplot.build_info.__file__)[0] + '.py'
        with open(installed_build_info_filename,'w') as module_fp:
            module_fp.write(avoplot.SRC_FILE_HEADER)
            module_fp.write('\n#This file is auto-generated by the %s '
                            'setup.py script.\n\n'%avoplot.PROG_SHORT_NAME)
            
            if sys.platform == "linux2":
                #we want our sys_runtime_files dir to be in prefix/share
                #global DATA_DIR
                DATA_DIR = os.path.join(install_paths['install_data'], 'share')
                module_fp.write("DATA_DIR = r'%s'\n"%DATA_DIR)
            else:
                #global DATA_DIR
                DATA_DIR =iobj.install_data.rstrip('\\')
                module_fp.write("DATA_DIR = r'%s'\n" %DATA_DIR)
                
            module_fp.write("LIB_DIR = r'%s'\n"%(install_paths['lib_dir'].rstrip('\\')))
            module_fp.write("SCRIPT_DIR = r'%s'\n"%(install_paths['script_dir'].rstrip('\\')))
        
        #now the build_info.py file will have been populated, so re-import it
        if os.path.exists(installed_build_info_filename+'c'):
            os.remove(installed_build_info_filename+'c') #remove the old compiled file first
        reload(avoplot)
        reload(avoplot.build_info)
        
        if sys.platform == "linux2":
            create_desktop_file()
            

#final tidy up - remove the autogenerated build info file from the source tree           
finally:
    os.remove(build_info_name)
    if os.path.exists(build_info_name+'c'):
        os.remove(build_info_name+'c') #remove compiled build_info file
