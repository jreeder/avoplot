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

import wx
import os
import inspect
import os.path
import warnings
from distutils.command.install import install
from distutils.core import setup as dist_utils_setup

import avoplot
from avoplot.figure import AvoPlotFigure

#dictionary to hold all plugins that get registered. Dict keys 
#are the names of the plugins
__plotting_plugins = {}


class PluginImportError(ImportError):
    """Exception class for plugin import errors"""
    pass


def is_plugin_gpl_compatible(plugin):
    """
    AvoPlot is released under the GPL license. A requirement of this license
    is that all plugins for AvoPlot are licensed in a GPL compatible way. This
    function looks in the module for 'plugin' (where plugin is an instance
    of the plugin class) for a variable called plugin_is_GPL_compatible and 
    returns its value. It returns False if plugin_is_GPL_compatible was not 
    defined in the module.
    
    See: 
    http://www.gnu.org/prep/standards/html_node/Dynamic-Plug_002dIn-Interfaces.html
    """
    #get the path of the .py file that the plugin is defined in
    plugin_module = inspect.getmodule(plugin.__class__)
    
    if hasattr(plugin_module, 'plugin_is_GPL_compatible'):
        return plugin_module.plugin_is_GPL_compatible

    return False



def register(plugin):
    """
    Registers a plugin with AvoPlot. This must be called from within
    the plugin when it is imported. The plugin argument should be an
    instance of the plugin class (which must be a subclass of AvoPlotPluginBase)
    """
    if not isinstance(plugin, AvoPlotPluginBase):
        raise PluginImportError("Failed to register plugin. Plugins must be a "
                           "subclass of AvoPlotPluginBase")
    
    #check plugin GPL compliance
    if not is_plugin_gpl_compatible(plugin):
        raise PluginImportError("Failed to register plugin \'%s\'. Plugins must"
                                " be GPL compatible. See the %s documentation "
                                "for details." %(plugin.name,
                                                 avoplot.PROG_SHORT_NAME))
    
    __plotting_plugins[plugin.name] = plugin
    
    

def get_plugin_install_path():
    """
    Returns the path where plug-ins should be installed. This will be the path
    that this module is in.
    """
    return __path__[0]



def get_plugins():
    """
    Returns a dict of {name:plugin}, where name is a string, and plugin
    is an instance of the plugin class (which should be a subclass of 
    AvoPlotPluginBase. If load_all_plugins() has not already been called,
    then the dict will be empty.
    """
    return __plotting_plugins



def load_plugin_from_file(filename):
    """
    Loads a plugin from a file. This function is for loading plugins which 
    have not been installed.
    """
    cur_dir = os.getcwd()
    os.chdir(os.path.dirname(filename))
    plugin = os.path.basename(filename)
    try:
        __import__(plugin.rstrip(".py"),
                   globals=globals(),
                   locals=locals())
    except Exception, e:
        #skip over any plugins that we cannot import
        warnings.warn('Failed to import plug-in \'%s\'. \n\nregister() '
                      'raised the exception: \'%s\'.' % (plugin, e.args[0]))
    
    #return to the old working dir
    os.chdir(cur_dir)
    
    
    
def load_all_plugins():
    """
    Loads all installed AvoPlot plug-ins. Plugins that cannot be loaded
    will be skipped and a warning message issued.
    """
    # import all the plugins from the plugins directory
    plugins_directory = __path__[0]
    
    cur_dir = os.getcwd()
    os.chdir(plugins_directory)
    
    #only attempt to import python files and directories
    plugin_list = [f for f in os.listdir(os.path.curdir) if (os.path.isdir(f) or 
                                                             f.endswith('.py'))]
    
    for plugin in plugin_list:
        try:
            __import__("avoplot.plugins." + plugin.rstrip(".py"),
                       fromlist=["avoplot.plugins"], globals=globals(),
                       locals=locals())
        except Exception, e:
            #skip over any plugins that we cannot import
            warnings.warn('Failed to import plug-in \'%s\'. \n\nregister() '
                          'raised the exception: \'%s\'.' % (plugin, e.args[0]))
        
    #return to the old working dir
    os.chdir(cur_dir)



class AvoPlotPluginBase(object):
    """
    Base class for AvoPlot plugins. 
    """
    def __init__(self, name, series_type):
        self.name = name
        self.__supported_series_type = series_type
        self._plots_in_single_axes = False
        self._menu_entry_labels = []
        self._menu_entry_tooltip = ""
        self._controls = []
        
    
    def get_supported_series_type(self):
        return self.__supported_series_type
        
        
    def get_controls(self):
        return self._controls
    
    
    def get_menu_entry_labels(self):
        return self._menu_entry_labels
    
    
    def get_menu_entry_tooltip(self):
        return self._menu_entry_tooltip
       
       
    def get_parent(self):
        return wx.GetApp().GetTopWindow() 


    def set_menu_entry(self, labels, tooltip):
        if type(labels) not in (list, tuple):
            raise TypeError("labels must be a list or tuple of strings")
        
        for s in labels:
            if type(s) != str:
                raise TypeError("labels must be a list or tuple of strings") 
        
        self._menu_entry_labels = labels
        self._menu_entry_tooltip = tooltip



class AvoPlotPluginSimple(AvoPlotPluginBase):
    """Base class for plugins only requiring a single subplot"""
    def __init__(self, name, series_type):
        super(AvoPlotPluginSimple, self).__init__(name, series_type)
        self._plots_in_single_axes = True
    
        #make sure that the derived class has defined the correct methods
        if not hasattr(self, 'plot_into_subplot'):
            raise RuntimeError("Plugins subclassed from AvoPlotPluginSimple "
                               "must define a plot_into_subplot(subplot)"
                               " method")
        
         
    def show_figure(self, fig, select=True):
        self.get_parent().add_figure(fig)
    
    
    def create_new(self, evnt):
        """
        Generate a new figure object, put a subplot into it,
        call plot_into_subplot() on the new subplot and then call
        show_figure() to add the new figure to the main window.
        """
        #create the new figure object
        fig = AvoPlotFigure(self.get_parent(), "New Figure")
                
        #figure out what type of subplot we need, based on what data
        #types the plugin supports
        data_type = self.get_supported_series_type()
        subplot_type = data_type.get_supported_subplot_type()
        
        #create the subplot instance
        subplot = subplot_type(fig, "New Subplot")
        
        #now plot the data into the subplot
        if not self.plot_into_subplot(subplot):
            return
        
        #add the figure as a tab in the main window
        self.show_figure(fig)
    
    
    
class AvoPlotPluginInstaller(install):
    """Specialised installer for AvoPlot plug-ins."""

    def finalize_options (self):
        """
        Overrides the finalize_options() method of the distutils install
        class. Ignores any user defined installation directories and sets the
        install path to be the AvoPlot plugins directory (as returned by 
        get_plugin_install_path())
        """
        ignored_opts = [self.prefix,
                        self.exec_prefix,
                        self.home,
                        self.install_base,
                        self.install_platbase,
                        self.root,
                        self.install_purelib,
                        self.install_platlib,
                        self.install_lib,
                        self.install_scripts]
        
        if self.__dict__.has_key('prefix_option'):
            #slightly older versions of distutils don't have this
            ignored_opts.append(self.prefix_option)
        
        for opt in ignored_opts:
            if opt is not None:
                self.warn("All installation path options are being ignored.")
                break
        
        if self.__dict__.has_key('prefix_option'):
            self.prefix_option = None
            
        self.prefix = None
        self.exec_prefix = None
        self.home = None
        self.install_base = None
        self.install_platbase = None
        self.root = None
        self.install_purelib = None
        self.install_platlib = None
        
        self.install_lib = get_plugin_install_path()
        self.install_scripts = get_plugin_install_path()
        
        install.finalize_options(self)
 


def setup(*args, **kwargs):
    """
    Replacement for the distutils.core setup function, to be used in setup.py
    files for AvoPlot plugins. It works exactly the same as the distutils 
    function except that it will set the install path for the plugin to be the 
    plugins  directory of AvoPlot (i.e. the path returned by 
    get_plugin_install_path()).
    """
    if kwargs.has_key('cmdclass'):
        if kwargs['cmdclass'].has_key('install'):  
            raise RuntimeError("Cannot override cmdclass install entry when "
                               "installing AvoPlot plugins.")
    
    #call the distutils setup function with our customised installer
    kwargs['cmdclass'] = {'install':AvoPlotPluginInstaller}
    dist_utils_setup(*args, **kwargs)

        
