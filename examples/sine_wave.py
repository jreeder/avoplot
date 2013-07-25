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
This module provides a simple example plugin for AvoPlot, which just
plots sin(x) over the range 0 <= x < 7. The plugin can be installed 
using the example_plugins_setup.py file which should be in the same 
folder as this file. To install, use the following commands:

     python example_plugins_setup.py build
     python example_plugins_setup.py install
     
The second of these commands will require administrative rights.
"""

#import the modules we need
import numpy
from avoplot import plugins, series

#conform to GPL license, otherwise AvoPlot will not load our plugin!
plugin_is_GPL_compatible = True


class ExamplePlugin(plugins.AvoPlotPluginSimple):
        #Define our plugin class. Plugins that only need to work with a single
        #subplot (i.e. one set of axes) should inherit from AvoPlotPluginSimple.
        
        def __init__(self):
        
            #call the base class __init__ method, telling it the name of our
            #plugin and also what type of data series it is designed to work
            #with
            super(ExamplePlugin, self).__init__("Example Plugin", 
                                                series.XYDataSeries)
            
            #create the menu entries for the File->New menu.
            self.set_menu_entry(['Examples','Sine Wave'], 
                                "Plot a sine wave")
        
        
        def plot_into_subplot(self, subplot):
            #this is where all the hard work of plotting gets done. For this
            #plugin we just create some simple data, but if you need to load
            #data files or request user input, then this is the place to do it
            
            #create our sine wave data
            x_data = numpy.linspace(0, 7, 500)
            y_data = numpy.sin(x_data)
            
            #wrap the data in a data series object. Note that the data series
            #used here should be the same type as we passed to the base class
            #__init__ method above
            data_series = series.XYDataSeries("sine wave", xdata=x_data, 
                                              ydata=y_data)
            
            #actually plot the data into the subplot
            subplot.add_data_series(data_series)
            
            #return True to indicate that all the plotting went ok and that we 
            #want AvoPlot to display our plot. If you return False here, then 
            #the plot will be discarded.
            return True


#register our plugin with AvoPlot so that it is available on startup. This line
#must be executed on import of your plugin file, so if you define your plugins
#in a package rather than a module, then the register() calls should be placed in 
#the __init__.py file.
plugins.register(ExamplePlugin())
