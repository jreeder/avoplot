#! python
# -*- coding: utf-8 -*-

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
import sys
import shutil

import avoplot
import avoplot.build_info

desktop_folder = get_special_folder_path("CSIDL_DESKTOPDIRECTORY")
start_menu_folder = get_special_folder_path("CSIDL_STARTMENU")
avoplot_prog_name = avoplot.build_info.PROG_SHORT_NAME+'.lnk'

if sys.argv[1] == '-install':
    
    icon_path = os.path.join(avoplot.get_avoplot_icons_dir(),'avoplot.ico')
    script_path = os.path.join(avoplot.build_info.SCRIPT_DIR,'AvoPlot.py')
    
    create_shortcut(
        os.path.join(sys.prefix, 'pythonw.exe'), # program
        avoplot.SHORT_DESCRIPTION, # description
        avoplot_prog_name, # filename
        script_path, # parameters
        '', # workdir
        icon_path, # iconpath
    )
    # move shortcut from current directory to DESKTOP_FOLDER
    shutil.move(os.path.join(os.getcwd(), avoplot_prog_name),
                os.path.join(start_menu_folder, avoplot_prog_name))
    
    # tell windows installer that we created another
    # file which should be deleted on uninstallation
    file_created(os.path.join(start_menu_folder, avoplot_prog_name))

if sys.argv[1] == '-remove':
    pass
    # This will be run on uninstallation. Nothing to do.