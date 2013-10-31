import numpy
import matplotlib.pyplot as plt
import math
from avoplot import plugins, series, controls, subplots
from avoplot.gui import widgets
import wx


plugin_is_GPL_compatible = True


class TrigFuncSubplot(subplots.AvoPlotXYSubplot):
    def my_init(self):
        """
        When defining your own subplot classes, you should not need to override
        the __init__ method of the base class. Instead you should define a 
        my_init() method which takes no args. This will be called automatically
        when the subplot is created. Use this to customise the subplot to suit 
        your specific needs - settings titles, axis formatters etc.
        """
        
        #call the parent class's my_init() method. This is not required, unless 
        #you want to make use of any customisation done by the parent class.
        #Note that this includes any control panels defined by the parent class!
        super(TrigFuncSubplot, self).my_init()
        
        #set up some axis titles
        ax = self.get_mpl_axes()
        ax.set_xlabel(r'$\theta$ (radians)')
        ax.set_ylabel('y')
        
        #add the units control panel to this subplot to allow the user to change
        #the x-axis units.
        self.add_control_panel(TrigSubplotUnitsCtrl(self))
        
        #set the initial name of the subplot
        self.set_name("Trig. Function Subplot")
        
        
        
class SineWaveSeries(series.XYDataSeries):
    """
    Define our own data series type for Sine data. Unlike for subplots, when 
    defining custom data series, we do override the __init__ method.
    """
    def __init__(self, *args, **kwargs):
        super(SineWaveSeries, self).__init__(*args, **kwargs)
        
        #add a control for this data series to allow the user to change the 
        #frequency of the wave using a slider.
        self.add_control_panel(SineWaveFreqCtrl(self))
    
    
    @staticmethod
    def get_supported_subplot_type():
        """
        This is how we restrict which data series can be plotted into which 
        types of subplots. Specialised subplots may provide controls for dealing
        with very specific types of data - for example, our TrigFuncSubplot 
        allows the x-axis to be switched between degrees and radians, it would
        therefore make no sense to allow time series data to be plotted into it.
        However, it might make sense to allow a SineWaveSeries to be plotted 
        into a general AvoPlotXYSuplot, and therefore this is permitted by 
        AvoPlot. The rule is as follows:
        
          A data series may be plotted into a subplot if the subplot is an
          instance of the class returned by its get_supported_subplot_type()
          method or any of its base classes.
        """
        return TrigFuncSubplot
        


class AdvExamplePlugin(plugins.AvoPlotPluginSimple):
        """
        This class is the same as that used for the Sine wave example, except
        that we use the SineWaveSeries data series class that we defined above
        rather than the generic XYDataSeries class used before.
        """
        def __init__(self):
            super(AdvExamplePlugin, self).__init__("Example Plugin with Controls",
                                                   SineWaveSeries)
        
            self.set_menu_entry(['Examples', 'Adv. Sine Wave'],
                                "Plot a sine wave with variable frequency")
            
        
        
        def plot_into_subplot(self, subplot):
            
            x_data = numpy.linspace(0, 7, 500)
            y_data = numpy.sin(x_data)
            
            data_series = SineWaveSeries("adv sine wave", xdata=x_data,
                                         ydata=y_data)
            
            subplot.add_data_series(data_series)
            
            return True


def rad2deg(theta, pos):
    """
    Function for converting radians to degrees for use with matplotlib's
    FuncFormatter object.
    """
    return '%0.2f'%math.degrees(theta)


class TrigSubplotUnitsCtrl(controls.AvoPlotControlPanelBase):
    """
    Control panel for trig function subplots allowing their x axis units
    to be changed from radians to degrees.
    """
    
    def __init__(self, subplot):
        
        #call the parent class's __init__ method, passing it the name that we
        #want to appear on the control panels tab.
        super(TrigSubplotUnitsCtrl, self).__init__("Units")
        
        #store the subplot object that this control panel is associated with, 
        #so that we can access it later
        self.subplot = subplot
    
    
    def setup(self, parent):
        """
        This is where all the controls get added to the control panel. You 
        *must* call the setup method of the parent class before doing any of
        your own setup.
        """
        #call parent class's setup method - do this before anything else
        super(TrigSubplotUnitsCtrl, self).setup(parent)
        
        #create a choice box for the different units for the x axis
        #we use a avoplot.gui.widgets.ChoiceSetting object which is a
        #thin wrapper around a wx.ChoiceBox, but provides a label and 
        #automatically registers the event handler.
        units_choice = widgets.ChoiceSetting(self, "x-axis units:", "Radians", 
                                             ["Radians", "Degrees"], 
                                             self.on_units_change)
        
        #add the choice widget to the control panel sizer
        self.Add(units_choice, 0,wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=10)
        
        
    def on_units_change(self, evnt):
        """
        Event handler for change of x axis units events.
        """
        #get the matplotlib axes object from the subplot
        ax = self.subplot.get_mpl_axes()
        
        #change the axis labels and label formatting based on the choice of
        #units
        if evnt.GetString() == 'Degrees':
            ax.set_xlabel(r'$\theta$ (degrees)')
            ax.xaxis.set_major_formatter(plt.FuncFormatter(rad2deg))
        else:
            ax.set_xlabel(r'$\theta$ (radians)')
            ax.xaxis.set_major_formatter(plt.ScalarFormatter())
        
        #draw our changes in the display
        self.subplot.update()
    


class SineWaveFreqCtrl(controls.AvoPlotControlPanelBase):
    """
    Control panel for sine wave data series allowing their frequency to 
    be changed using a slider.
    """
    def __init__(self, series):
        #call the parent class's __init__ method, passing it the name that we
        #want to appear on the control panels tab.
        super(SineWaveFreqCtrl, self).__init__("Freq.")
        
        #store the data series object that this control panel is associated with, 
        #so that we can access it later
        self.series = series
    
    
    def setup(self, parent):
        """
        This is where all the controls get added to the control panel. You 
        *must* call the setup method of the parent class before doing any of
        your own setup.
        """
        
        #call parent class's setup method - do this before anything else
        super(SineWaveFreqCtrl, self).setup(parent)
        
        #create a label for the slider
        label = wx.StaticText(self, wx.ID_ANY, 'Frequency')
        self.Add(label, 0,
                 wx.LEFT | wx.RIGHT | wx.TOP | wx.ALIGN_CENTER_HORIZONTAL,
                 border=10)
        
        #create a frequency slider
        self.slider = wx.Slider(self, wx.ID_ANY, value=1, minValue=1,
                                maxValue=30, style=wx.SL_LABELS)
        
        #add the slider to the control panel's sizer
        self.Add(self.slider, 0, 
                 wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, border=10)
        
        #register an event handler for slider change events
        wx.EVT_COMMAND_SCROLL(self, self.slider.GetId(), self.on_slider_change)
    
    
    def on_slider_change(self, evnt):
        """
        Event handler for frequency slider change events.
        """
        
        #change the frequency of the sine wave data accordingly
        f = self.slider.GetValue()
        x_data = numpy.linspace(0, 7, 2000)
        y_data = numpy.sin(x_data * f)
        
        #change the data in the series object
        self.series.set_xy_data(xdata=x_data, ydata=y_data)
        
        #draw our changes on the display
        self.series.update()
        
        
        
#register the plugin with AvoPlot
plugins.register(AdvExamplePlugin())
