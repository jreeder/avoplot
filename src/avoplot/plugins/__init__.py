import wx
import os
import os.path
import warnings
from distutils.command.install import install
from distutils.core import setup as dist_utils_setup

__plotting_plugins = {}


def register(plugin):
    """
    Registers a plugin with AvoPlot. This must be called from within
    the plugin when it is imported. The plugin argument should be an
    instance of the plugin class (which must be a subclass of AvoPlotPluginBase)
    """
    #TODO
    #if not issubclass(plugin, AvoPlotPluginBase):
    #    raise RuntimeError("Failed to register plugin. Plugins must be a subclass of AvoPlotPluginBase")
    __plotting_plugins[plugin.name] = plugin
    

def get_plugin_install_path():
    """
    Returns the path where plug-ins should be installed.
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
    plugin_list = [f for f in os.listdir(os.path.curdir) if os.path.isdir(f) or f.endswith('.py')]
    
    for plugin in plugin_list:
        try:
            __import__("avoplot.plugins."+plugin.rstrip(".py"), 
                       fromlist=["avoplot.plugins"], globals=globals(), 
                       locals=locals())
        except ImportError:
            warnings.warn("Failed to import plug-in \'"+plugin+'\'.')
        
    #return to the old working dir
    os.chdir(cur_dir)


class AvoPlotPluginBase:
    """
    Base class for AvoPlot plugins. All plugins should inherit from this class.
    """
    def __init__(self, name):
        self.name = name
    
    
    def add_plot_to_main_window(self, plot, name, select=True):
        self.get_parent().add_plot_tab(plot, name, select=select)
    
    
    def get_parent(self):
        return wx.GetApp().GetTopWindow() 
    
    
    def get_onNew_handler(self):
        #TODO - write a sensible doc string for this
        """

        """
        raise NotImplementedError("AvoPlotPluginBase must be subclassed.")
    
    
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
                        self.prefix_option,
                        self.install_base,
                        self.install_platbase,
                        self.root,
                        self.install_purelib,
                        self.install_platlib,
                        self.install_lib,
                        self.install_scripts]
        
        for opt in ignored_opts:
            if opt is not None:
                self.warn("All installation path options are being ignored.")
                break
        
        self.prefix = None
        self.exec_prefix  = None
        self.home = None
        self.prefix_option = None
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
    files for AvoPlot plugins. It works exactly the same as the distutils function
    except that it will set the install path for the plugin to be the plugins 
    directory of AvoPlot (i.e. the path returned by get_plugin_install_path()).
    """
    if kwargs.has_key('cmdclass'):
        if kwargs['cmdclass'].has_key('install'):  
            raise RuntimeError("Cannot override cmdclass install entry when installing AvoPlot plugins.")
    
    #call the distutils setup function with our customised installer
    kwargs['cmdclass'] = {'install':AvoPlotPluginInstaller}
    dist_utils_setup(*args, **kwargs)

        