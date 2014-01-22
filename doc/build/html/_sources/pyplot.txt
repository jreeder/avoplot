Scripting Interface
===================

.. note:: The AvoPlot scripting interface is a new feature, and cannot be considered "stable" yet. Only a very limited amount of functionality has been implemented so far and I would welcome any feedback/bug reports that people have.

The scripting interface is designed to mimic matplotlib_'s pylab interface. In this way, it is hoped that users will find it easy to transition from using the plot viewer included with matplotlib_ to using AvoPlot. The call signatures of all the AvoPlot functions are the same as their matplotlib_ counterparts, however, the AvoPlot versions currently all return None - this may be changed in the future.

The example below shows how to create a simple figure using AvoPlot's scripting interface. Users who are familiar with matplotlib_ should find no great surprises here, others are recommended to check out the excellent documentation/tutorials that are available for matplotlib_ first.

.. code-block:: python

    import avoplot.pyplot as plt
    import numpy
    
    #create some data to plot, in this case a sine wave
    x_data = numpy.linspace(0, 13, 1000)
    y_data = numpy.sin(x_data)
    
    #plot the data as a red line
    plt.plot(x_data, y_data, 'r-')
    
    #set the plot title and axis labels
    plt.title('My first scripted AvoPlot figure')
    plt.xlabel(r'$\theta$ (radians)')
    plt.ylabel(r'sin($\theta$)')
    
    #display the plot
    plt.show()
    
    #note that show() is non-blocking - AvoPlot remains open after 
    #the script exits though
    print 'Script finished (but your plot will stay open).'

.. _matplotlib: http://matplotlib.org/
