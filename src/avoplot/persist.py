import atexit
import os.path
import cPickle

import avoplot

_persistant_storage = None

class __PersistantStorage:
    """
    Class for storing non-volatile settings (i.e. those that you want to be
    available the next time you start the program). The actual settings just 
    get pickled and stored in the AvoPlot read/write directory (as returned by
    avoplot.get_avoplot_rw_dir()). To prevent multiple instances of this class
    overwriting each others data, you should not instanciate the class directly, 
    instead use the PersistantStorage function which simply hands out references 
    to a single instance.
    """
    def __init__(self):
        #setup save_settings to be run when the program exits.
        atexit.register(self._save_settings)
        
        self.__cache_file = os.path.join(avoplot.get_avoplot_rw_dir(),"avoplot.persist")
        
        #attempt to load the persistant settings from the cache - give up if we can't
        try:
            with open(self.__cache_file,"rb") as ifp:
                self.__settings = cPickle.load(ifp)
        
        except:
            self.__settings = {}
        
               
    def _save_settings(self):
        """
        Writes the settings to file. Should not be called directly.
        """
        try:
            with open(self.__cache_file,"wb") as ofp:
                cPickle.dump(self.__settings, ofp)
        except Exception,e:
            print e.args
            pass

    
    def get_value(self, name):
        """
        Returns the value of the setting with the specified name. 
        Raises KeyError if no setting with this name exists.
        """
        return self.__settings[name]

    
    def set_value(self, name, value):
        """
        Sets the value of the specified setting. "name" must be a hashable
        object.
        """
        self.__settings[name] = value

        
def PersistantStorage():
    """
    Returns a reference to the global persistant storage class. Which can be 
    used for storing settings across program restarts.
    """
    if globals()['_persistant_storage'] is None:
        globals()['_persistant_storage'] = __PersistantStorage()
    return globals()['_persistant_storage']
