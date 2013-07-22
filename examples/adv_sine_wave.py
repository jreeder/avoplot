import numpy
from avoplot import plugins, series, controls
import wx


plugin_is_GPL_compatible = True


class SineWaveSeries(series.XYDataSeries):
    def __init__(self, *args, **kwargs):
        super(SineWaveSeries, self).__init__(*args, **kwargs)
        self.add_control_panel(SineWaveFreqCtrl(self))
        

class AdvExamplePlugin(plugins.AvoPlotPluginSimple):
        def __init__(self):
            super(AdvExamplePlugin, self).__init__("Example Plugin with Controls", 
                                                series.XYDataSeries)
        
            self.set_menu_entry(['Examples','Adv. Sine Wave'], 
                                "Plot a sine wave with variable frequency")
            
        
        
        def plot_into_subplot(self, subplot):
            
            x_data = numpy.linspace(0, 7, 500)
            y_data = numpy.sin(x_data)
            
            data_series = SineWaveSeries("adv sine wave", xdata=x_data, 
                                              ydata=y_data)
            
            subplot.add_data_series(data_series)
            
            return True


class SineWaveFreqCtrl(controls.AvoPlotControlPanelBase):
    
    def __init__(self, series):
        super(SineWaveFreqCtrl, self).__init__("Freq.")
        self.series = series
    
    
    def setup(self, parent):
        super(SineWaveFreqCtrl, self).setup(parent)
        
        #create a label for the slider
        label = wx.StaticText(self, wx.ID_ANY, 'Frequency')
        self.Add(label, 0, wx.LEFT | wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, border=10)
        
        #create a frequency slider
        self.slider = wx.Slider(self, wx.ID_ANY, value=1, minValue=1, maxValue=30, style=wx.SL_LABELS)
        
        self.Add(self.slider, 0, wx.ALL| wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, border=10)
        wx.EVT_COMMAND_SCROLL_CHANGED(self, self.slider.GetId(),self.on_slider_change)
    
    
    def on_slider_change(self, evnt):
        
        f = self.slider.GetValue()
        x_data = numpy.linspace(0, 7, 2000)
        y_data = numpy.sin(x_data*f)
        
        self.series.set_xy_data(xdata=x_data, ydata=y_data)
        l, = self.series.get_mpl_lines()
        l.axes.figure.canvas.draw() 
        

plugins.register(AdvExamplePlugin())
