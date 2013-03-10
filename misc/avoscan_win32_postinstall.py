#! python
# -*- coding: utf-8 -*-

import os
import sys
import shutil

desktop_folder = get_special_folder_path("CSIDL_DESKTOPDIRECTORY")
start_menu_folder = get_special_folder_path("CSIDL_STARTMENU")
avoscan_prog_name = 'AvoScan.lnk'
avoplot_prog_name = 'AvoPlot.lnk'

if sys.argv[1] == '-install':
    icon_path = os.path.join(sys.prefix,'icons','avoscan.ico')
    script_path = os.path.join(sys.prefix,'Scripts','AvoScan.py')
    
    create_shortcut(
        os.path.join(sys.prefix, 'pythonw.exe'), # program
        'Control AvoScanner DOAS scanning units', # description
        avoscan_prog_name, # filename
        script_path, # parameters
        '', # workdir
        icon_path, # iconpath
    )
    # move shortcut from current directory to DESKTOP_FOLDER
    shutil.move(os.path.join(os.getcwd(),avoscan_prog_name),
                os.path.join(desktop_folder, avoscan_prog_name))
    
    # tell windows installer that we created another
    # file which should be deleted on uninstallation
    file_created(os.path.join(desktop_folder, avoscan_prog_name))
    
    
    icon_path = os.path.join(sys.prefix,'icons','avoplot.ico')
    script_path = os.path.join(sys.prefix,'Scripts','AvoPlot.py')
    
    create_shortcut(
        os.path.join(sys.prefix, 'pythonw.exe'), # program
        'Visualise DOAS data', # description
        avoplot_prog_name, # filename
        script_path, # parameters
        '', # workdir
        icon_path, # iconpath
    )
    # move shortcut from current directory to DESKTOP_FOLDER
    shutil.move(os.path.join(os.getcwd(), avoplot_prog_name),
                os.path.join(desktop_folder, avoplot_prog_name))
    
    # tell windows installer that we created another
    # file which should be deleted on uninstallation
    file_created(os.path.join(desktop_folder, avoplot_prog_name))

if sys.argv[1] == '-remove':
    pass
    # This will be run on uninstallation. Nothing to do.
