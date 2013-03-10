import atexit
import os.path
import cPickle

import avoscan


class PersistantStorage:
    def __init__(self):
        #setup save_settings to be run when the program exits.
        atexit.register(self.save_settings)
        
        self.__cache_file = os.path.join(avoscan.get_avoscan_rw_dir(),"AvoPlot","avoplot.persist")
        
        #attempt to load the persistant settings from the cache - give up if we can't
        try:
            with open(self.__cache_file,"rb") as ifp:
                self.settings = cPickle.load(ifp)
        
        except:
            self.settings = {}
        
               
    def save_settings(self):
        try:
            with open(self.__cache_file,"wb") as ofp:
                cPickle.dump(self.settings, ofp)
        except Exception,e:
            print e.args
            pass

    
    def get_value(self, name):
        return self.settings[name]

    
    def set_value(self, name, value):
        self.settings[name] = value