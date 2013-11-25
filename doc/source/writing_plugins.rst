Writing Plugins
===============

The whole point of AvoPlot is to provide a plotting interface that can be easily extended to deal with specific types of data. To facilitate this, AvoPlot provides a plugin interface which allows end-users to create plugins that not only import data into AvoPlot, but also provide tools for manipulating it. Writing plugins for AvoPlot is relatively straightforward, but there are several steps that need to be followed. These are best explained by example.

A Simple Example
----------------

As a simple example of writing a plugin, lets create a plugin that plots a sine wave. The complete plugin file for this example can be found in the "examples" folder of the AvoPlot package. The contents of the file looks like this:


.. code-block:: python
    
    import numpy
    from avoplot import plugins, series


    plugin_is_GPL_compatible = True


    class ExamplePlugin(plugins.AvoPlotPluginSimple):
            def __init__(self):
                super(ExamplePlugin, self).__init__("Example Plugin", 
                                                    series.XYDataSeries)
            
                self.set_menu_entry(['Examples','Sine Wave'], 
                                    "Plot a sine wave")
            
            
            def plot_into_subplot(self, subplot):
                
                x_data = numpy.linspace(0, 7, 500)
                y_data = numpy.sin(x_data)
                
                data_series = series.XYDataSeries("sine wave", xdata=x_data, 
                                                  ydata=y_data)
                
                subplot.add_data_series(data_series)
                
                return True


    plugins.register(ExamplePlugin())


Now lets go through that step by step.

.. code-block:: python
    
    import numpy
    from avoplot import plugins, series
    
These lines just import the modules that we need for defining our plugin.

.. code-block:: python

    plugin_is_GPL_compatible = True

.. _here: http://www.gnu.org/prep/standards/html_node/Dynamic-Plug_002dIn-Interfaces.html
.. _GPL: http://www.gnu.org/licenses/gpl.html

AvoPlot is licensed under the terms of the Gnu Public License (GPL_). A requirement of this license is that plugins for AvoPlot must be licensed in a GPL_ compatible way (as discussed here_). By including this line in your plugin source file you are indicating that your plugin is licensed in a GPL compatible way. If you don't know what that means then take a look at the website for the GPL_. AvoPlot will not load your plugin if it does not include this line!

.. code-block:: python

    class ExamplePlugin(plugins.AvoPlotPluginSimple):

AvoPlot plugins are just Python objects. Simple plugins that only require one subplot (set of axes) should inherit from :py:class:`~avoplot.plugins.AvoPlotPluginSimple`.

.. code-block:: python

    super(ExamplePlugin, self).__init__("Example Plugin", 
                                        series.XYDataSeries)

If your plugin class defines and __init__ method, then you must call the __init__ method of the base class. You should pass it a descriptive name for your plugin, in this case "Example Plugin" and also the type of data series that your plugin is designed to work with - more on that later.

.. code-block:: python

    self.set_menu_entry(['Examples','Sine Wave'], 
                        "Plot a sine wave")

To get our plugin to show up in the AvoPlot menus, we need to call :py:meth:`~avoplot.plugins.AvoPlotPluginBase.set_menu_entry`. The first argument to this method, is a list of menu entries. The final entry in the list will be the menu entry for the plugin and the preceding entries will form submenus. So in the example above, we will get an 'Examples' submenu with a 'Sine Wave' entry. This allows us to group similar plugins together, for example if we wanted to create a cosine example as well then we might call set_menu_entry with ['Examples', 'Cosine Wave']. This would result in an 'Examples' submenu with 'Sine Wave' and 'Cosine Wave' entries. More nested menus can be created by simply extending the list e.g. ['Examples', 'Trig. Functions', 'Sine Wave'] etc. The second argument to set_menu_entry is the tooltip that will be displayed when the mouse is hovered over the menu entry.

.. code-block:: python

    def plot_into_subplot(self, subplot):
                
        x_data = numpy.linspace(0, 7, 500)
        y_data = numpy.sin(x_data)


If your plugin inherits from :py:class:`~avoplot.plugins.AvoPlotPluginSimple` then this is the only other method that you have to define. The subplot argument that is passed to the method will be an AvoPlot subplot object. This method is the place to do all of your data loading/processing etc. Basically, eveything you need to do before your data gets plotted. In our example we simply create some arrays of values, but you are free to open dialogs to get the user to select files, perform complex operations etc etc.

.. code-block:: python

    data_series = series.XYDataSeries("sine wave", xdata=x_data, 
                                      ydata=y_data)
                                     
Once we have our data, then we need to wrap it into a data series object. Since our sine wave is only has simple x,y data we use a :py:class:`~avoplot.series.XYDataSeries`. The first argument to the data series constructor is the name of the data that we are plotting.


.. code-block:: python

    subplot.add_data_series(data_series)
    
This line actually plots the data into the subplot.

.. code-block:: python

    return True

Finally, we should return True to tell AvoPlot that everything went ok with the plotting and that we want it to add our plot to the main window. If something goes wrong, and you decide at this point that you don't want to plot anything (for example the user clicks cancel in your file select dialog) then you should return False.

.. code-block:: python

        plugins.register(ExamplePlugin())

This registers the plugin with AvoPlot so that it can be used. This function must be called on import of your plugin file/package and takes an instance of your plugin class as its only argument.



Installing Your Plugin
----------------------

.. _distutils: http://docs.python.org/2/library/distutils.html

In order to use your plugins they will have to be installed. This is done in exactly the same way as you would for ordinary Python modules/packages, using distutils_. However, there is one important difference! Instead of using the setup function provided by distutils_ you should use the one provided by the avoplot.plugins modules e.g.:

.. code-block:: python

    from avoplot.plugins import setup

This can be used in exactly the same way as the distutils setup function. See the example_plugins_setup.py file in the "examples" folder of the AvoPlot distribution. To install all the example plugins change directory into AvoPlot/examples folder and run the command:::
    
    python example_plugins_setup.py install

Depending on where you installed AvoPlot, you may need administrative rights. You will need to re-start AvoPlot for the changes to take effect. The next time you start AvoPlot you will find new options under the `File->New` menu.


A More Advanced Example
-----------------------
This part of the documentation is still incomplete! For now, please refer to the adv_sine_wave.py file in the examples folder of the AvoPlot distribution. This shows how to create your own subplot and data series types and add controls to them. The file is well commented and should be self explanatory.

