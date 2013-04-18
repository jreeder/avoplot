import atexit
import os.path

import avoscan


_spectrometer_manager = None

def SpectrometerManager():
    """
    Returns a reference to the global spectrometer manager class. Which can be 
    used for storing spectrometer settings across program restarts.
    """
    if globals()['_spectrometer_manager'] is None:
        globals()['_spectrometer_manager'] = __SpectrometerManager()
    return globals()['_spectrometer_manager']

class Spectrometer:
    def __init__(self, name):
        self.name = name
        self._properties = {}
    
    def get_value(self, name):
        return self._properties[name]
    
    def set_value(self, name, value):
        self._properties[name] = value


class __SpectrometerManager:
    
    def __init__(self):
        
        self.__changed_spectrometers = set([])
        self.spectrometers = {}
        
        #setup an atexit function to write all the spectrometer data to file
        atexit.register(self._save_spectrometers)
        
        self.spectrometer_dir = os.path.join(avoscan.get_avoscan_rw_dir(),"Spectrometers")
        
        if not os.path.isdir(self.spectrometer_dir):
            os.makedirs(self.spectrometer_dir)
            
        #load all the spectrometers that are in the directory
        for spectrometer_file in os.listdir(self.spectrometer_dir):
            try:
                s = self.load_spectrometer_file(os.path.join(self.spectrometer_dir,spectrometer_file))
                
                self.spectrometers[s.name] = s
            except Exception, e:
                print "SpectrometerManager: Skipping file \""+spectrometer_file+"\"", e.args
    
    
    def get_spectrometer(self, name):
        try:
            return self.spectrometers[name]
        except KeyError:
            return Spectrometer(name)
    
    
    def update(self, spectrometer):
        """
        Call this if you change any parameters
        of the spectrometer.
        """
        self.spectrometers[spectrometer.name] = spectrometer
        self.__changed_spectrometers.add(spectrometer.name)
    
    
    def _save_spectrometers(self):
        
        for name in self.__changed_spectrometers:
            self.__write_spectrometer_to_file(self.spectrometers[name])
    
    
    def __write_spectrometer_to_file(self, spectrometer):
        with open(os.path.join(self.spectrometer_dir, spectrometer.name),'w') as ofp:
            ofp.write("#AvoScan Spectrometer File#\n")
            ofp.write("name = "+spectrometer.name+"\n")
            
            for key, value in spectrometer._properties.items():
                ofp.write(key + " = " + value+"\n")
    
    
    def load_spectrometer_file(self, filename):
        with open(filename,'r') as ifp:
            if not ifp.readline().startswith("#AvoScan Spectrometer File#"):
                raise IOError(filename+" is not a valid spectrometer file")
            
            file_contents = {}
            
            for line in ifp:
                if line == "" or line.isspace():
                    #skip blank lines
                    continue
                if line.startswith("#"):
                    #skip comment lines
                    continue
                if line.count("=") == 0:
                    continue
                
                key,sep,val = line.partition("=")
                
                #sanity check!
                if file_contents.has_key(key):
                    raise ValueError("Multiple values for \""+key+"\" in file \""+filename)
                
                file_contents[key.strip()] = val.strip()
        
        s = Spectrometer(file_contents.pop('name'))
        for key,value in file_contents.items():
            s.set_value(key,value)
        
        return s
                