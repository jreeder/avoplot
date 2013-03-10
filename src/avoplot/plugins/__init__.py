import os
import os.path


__plotting_plugins = {}


def register(plugin):
    """
    Registers a plugin with AvoPlot. This must be called from within
    the plugin when it is imported. The plugin argument should be an
    instance of the plugin class (which must be a subclass of AvoPlotPluginBase)
    """
    if not isinstance(plugin, AvoPlotPluginBase):
        raise RuntimeError("Failed to import plugin. Plugins must be a subclass of AvoPlotPluginBase")
    __plotting_plugins[plugin.name] = plugin
    

def get_plugins():
    return __plotting_plugins

    
def load_all_plugins():
    """
    Loads all installed AvoPlot plugins.
    """
    # import all the plugins from the plugins directory
    plugins_directory = __path__[0]
    
    cur_dir = os.getcwd()
    os.chdir(plugins_directory)
    
    for plugin_file in os.listdir(os.path.curdir):
        if plugin_file == "__init__.py":
            continue
        __import__("avoplot.plugins."+plugin_file.rstrip(".py"), 
                   fromlist=["avoplot.plugins"], globals=globals(), 
                   locals=locals())
        
    #return to the old working dir
    os.chdir(cur_dir)



class AvoPlotPluginBase:
    def __init__(self, name):
        self.name = name
    
    
    def get_plot_open_submenu(self, parent):
        """
        Returns a wx.Menu object which will be inserted into the File->New menu
        under the heading of the plugin name. The parent argument is the parent 
        window for the menu (so this allows you to set up all the event handlers).
        
        """
        return None
    
    
    
        