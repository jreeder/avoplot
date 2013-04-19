import wx
import os
import threading
import matplotlib
import datetime
import time

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

#from doas.spectrum_loader import SpectrumIO
#from doas import spectra_dir
#from doas import spectrum_loader
#from doas import spectrum_maths

from std_ops.os_ import find_files

def invalid_user_input(message):
        wx.MessageBox(message, "AvoPlot", wx.ICON_ERROR)



class PlotPanelBase(wx.ScrolledWindow):
    
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, wx.ID_ANY)
        self.SetScrollRate(2,2)
        self._is_panned = False
        self._is_zoomed = False
        self._gridlines = False
        
        self.parent = parent
        self.v_sizer = wx.BoxSizer(wx.VERTICAL)
        self.h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.h_sizer.Add(self.v_sizer, 1, wx.EXPAND)
        
        #the figure size is a bit arbitrary, but seems to work ok on my small screen - 
        #all this does is to set the minSize size hints for the sizer anyway.
        self.fig = Figure(figsize=(4,2))
        
        #set figure background to white
        #TODO - would this look better in default wx colour
        self.fig.set_facecolor((1,1,1))
        
        #try:
            #TODO - test this actually works on an up to date version of mpl
        #    matplotlib.pyplot.tight_layout()
        #except AttributeError:
            #probably an old version of mpl that does not have this function
        #    pass
        
        self.canvas = FigureCanvasWxAgg(self, -1, self.fig)
        
        self.tb = NavigationToolbar2Wx(self.canvas)
        self.tb.Show(False)

        self.v_sizer.Add(self.canvas, 1, wx.ALIGN_LEFT|wx.ALIGN_TOP|wx.EXPAND)
        
        self.SetSizer(self.h_sizer)
        self.h_sizer.Fit(self)
        self.SetAutoLayout(True)
                
        self.axes = self.fig.add_subplot(111)
        
        #self.plotting_thread = threading.Thread(target=self._create_plot)
        #self.plotting_thread.start()
    
    
    def close(self):
        #don't explicitly delete the window since it is managed by a notebook
        #self.plotting_thread.join()
        pass

        
    
    def go_home(self):
        self.axes.relim()
        self.axes.autoscale(enable=True)
        self.axes.autoscale_view()
        self.canvas.draw()
        self.canvas.gui_repaint()
 
    
    def zoom(self):
        self.tb.zoom()
        self._is_zoomed = not self._is_zoomed
        self._is_panned = False
    
    
    def pan(self):
        self.tb.pan()
        self._is_panned = not self._is_panned
        self._is_zoomed = False
    
    
    def gridlines(self, state):
        self.axes.grid(state)
        self._gridlines = state
        self.canvas.draw()
        self.canvas.gui_repaint()
    
    
    def save_plot(self):
        self.tb.save(None)


#class TimePlotSettingsFrame(wx.Dialog):
#    def __init__(self,parent, persistant, spectrometer_manager, name="Time plot settings"):
#        wx.Dialog.__init__(self, None, wx.ID_ANY, name)
#        
#        self.parent = parent
#        self.persist = persistant
#        self.spectrometer_manager = spectrometer_manager
#        
#        self.spec_dir = None
#        self.recursive = None
#        self.inband = None
#        self.outband = None
#        self.name = "Time plot"
#                
#        top_panel = wx.Panel(self, wx.ID_ANY)
#        self.vsizer = wx.BoxSizer(wx.VERTICAL)
#        
#        #add the directory browsing box/button
#        dirname_sizer = wx.BoxSizer(wx.HORIZONTAL)
#        self.browse_button = wx.Button(top_panel, wx.ID_ANY, "Browse")
#        #make filename box the same height as the button
#        self.dir_box = wx.TextCtrl(top_panel, wx.ID_ANY, size=(300,self.browse_button.GetSize()[1]))
#        dirname_sizer.Add(self.dir_box, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL)
#        dirname_sizer.Add(self.browse_button, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
#        
#        self.vsizer.Add(wx.StaticText(top_panel, wx.ID_ANY, "Spectrum directory:"), 0,wx.LEFT| wx.RIGHT| wx.TOP | wx.ALIGN_TOP, border=10)
#        self.vsizer.Add(dirname_sizer, 0, wx.LEFT| wx.RIGHT|wx.ALIGN_CENTER_HORIZONTAL| wx.EXPAND | wx.ALIGN_TOP, border=10)
#        
#        #add the recursive selection checkbox
#        self.recursive_check_box = wx.CheckBox(top_panel, wx.ID_ANY, "Search directory recursively")      
#        self.vsizer.Add(self.recursive_check_box,1, wx.ALL|wx.ALIGN_LEFT, border=10)
#        
#        #add spectra info text fields
#        self.spectrometer_id_txt = wx.StaticText(top_panel, wx.ID_ANY, "Spectrometer ID:")
#        self.num_of_spectra_txt = wx.StaticText(top_panel, wx.ID_ANY, "Number of spectra:")
#        self.start_time_txt = wx.StaticText(top_panel, wx.ID_ANY, "Start Time:")
#        self.end_time_txt = wx.StaticText(top_panel, wx.ID_ANY, "End Time:")
#        
#        self.vsizer.AddSpacer(10)
#        self.vsizer.Add(self.spectrometer_id_txt,0,wx.ALIGN_LEFT|wx.LEFT, border=10)
#        self.vsizer.Add(self.num_of_spectra_txt,0,wx.ALIGN_LEFT|wx.LEFT, border=10)
#        self.vsizer.Add(self.start_time_txt,0,wx.ALIGN_LEFT|wx.LEFT, border=10)
#        self.vsizer.Add(self.end_time_txt,0,wx.ALIGN_LEFT|wx.LEFT, border=10)
#        self.spectrometer_id_txt.Disable()
#        self.num_of_spectra_txt.Disable()
#        self.start_time_txt.Disable()
#        self.end_time_txt.Disable()
#        self.vsizer.AddSpacer(10)
#        
#        #add the inband wavelength selection
#        inband_sizer = wx.BoxSizer(wx.HORIZONTAL)
#        self.inband_box = wx.TextCtrl(top_panel, wx.ID_ANY)
#        inband_sizer.Add(wx.StaticText(top_panel, wx.ID_ANY, "Wavelength within SO2 band:"),0,wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
#        inband_sizer.AddSpacer(5)
#        inband_sizer.Add(self.inband_box, 0, wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, border=10)
#        self.vsizer.Add(inband_sizer,1,wx.ALIGN_RIGHT)
#               
#        #add the outband wavelength selection
#        outband_sizer = wx.BoxSizer(wx.HORIZONTAL)
#        self.outband_box = wx.TextCtrl(top_panel, wx.ID_ANY)
#        outband_sizer.Add(wx.StaticText(top_panel, wx.ID_ANY, "Wavelength outside SO2 band:"),0,wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
#        outband_sizer.AddSpacer(5)
#        outband_sizer.Add(self.outband_box, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, border=10)
#        self.vsizer.Add(outband_sizer,1,wx.ALIGN_RIGHT)  
#        
#        #add the ok and cancel buttons
#        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
#        self.ok_button = wx.Button(top_panel, wx.ID_ANY, "Ok")
#        self.cancel_button = wx.Button(top_panel, wx.ID_ANY, "Cancel")
#        
#        button_sizer.Add(self.cancel_button, 0, wx.ALIGN_RIGHT| wx.ALIGN_BOTTOM)
#        button_sizer.Add(self.ok_button, 0, wx.ALIGN_RIGHT| wx.ALIGN_BOTTOM)
#        self.vsizer.Add(button_sizer, 1, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT| wx.ALL, border=10)   
#        
#        top_panel.SetSizer(self.vsizer)      
#        top_panel.SetAutoLayout(1)
#        self.vsizer.Fit(self)
#        
#        wx.EVT_BUTTON(self, self.browse_button.GetId(),self.onBrowse)
#        wx.EVT_BUTTON(self, self.ok_button.GetId(),self.onOK)
#        wx.EVT_BUTTON(self, self.cancel_button.GetId(),self.onCancel)
#        wx.EVT_CLOSE(self, self.onCancel)
#        self.CenterOnScreen()
#        
#        
#    def get_plot(self):
#        if None in (self.recursive, self.inband, self.outband, self.name):
#            raise RuntimeError("get_plot called before values have been set")
#        return TimePlot(self.parent, self.spec_dir, self.inband, self.outband, self.recursive)
#    
#    
#    def get_name(self):
#        return self.name
#    
#    def onOK(self,evnt):
#        self.recursive = self.recursive_check_box.IsChecked()
#        self.spec_dir = self.dir_box.GetValue()
#        if self.spec_dir == "":
#            self.spec_dir = None
#            invalid_user_input("No spectrum directory specified.")
#            return
#        if not os.path.isdir(self.spec_dir):
#            invalid_user_input("Cannot open \""+self.spec_dir+"\". No such directory.")
#            self.spec_dir = None
#            return
#        
#        self.inband = self.inband_box.GetValue()
#        if self.inband == "":
#            self.inband = None
#            invalid_user_input("No in-band wavelength specified.")
#            return
#
#        try:
#            self.inband = float(self.inband)
#        except ValueError:
#            self.inband = None
#            invalid_user_input("Invalid value for in-band wavelength.")
#            return
#        
#        self.outband = self.outband_box.GetValue()
#        if self.outband == "":
#            self.outband = None
#            invalid_user_input("No out of band wavelength specified.")
#            return
#
#        try:
#            self.outband = float(self.outband)
#        except ValueError:
#            self.outband = None
#            invalid_user_input("Invalid value for out of band wavelength.")
#            return
#        
#        self.EndModal(wx.OK)
#        self.Destroy()
#
#    
#    def onCancel(self, evnt):
#        self.EndModal(wx.CANCEL)
#        self.Destroy()
#
#    
#    def onBrowse(self, evnt):
#        try:
#            last_path_used = self.persist.get_value("spectra_dir")
#            #want the parent directory of the spec_dir
#            last_path_used = os.path.join(last_path_used, os.path.pardir)
#        except KeyError:
#            last_path_used = ""
#        
#        spec_dir = wx.DirSelector("Choose spectrum directory", defaultPath=last_path_used)
#
#        if spec_dir == "":
#            return
#        wx.BeginBusyCursor()
#        wx.Yield()
#        try:
#            self.persist.set_value("spectra_dir", spec_dir)
#            self.dir_box.SetValue(spec_dir)
#            
#            #TODO - don't use a spectrum iterator here - use a metadata parser
#            #TODO - spectrum iterator should only be updated if the spec_dir has changed
#            if self.recursive_check_box.IsChecked():
#                spec_files = find_files(spec_dir, recursive=True)
#            else:
#                spec_files = [os.path.join(spec_dir, n) for n in os.listdir(spec_dir)]
#            
#            spec_loader = spectrum_loader.SpectrumIO()
#            first_spec = None
#            last_spec = None
#            first_spec_index = 0
#            for f in spec_files:
#                try:
#                    first_spec = spec_loader.load(f)
#                    first_spec_index += 1
#                    break
#                except spectrum_loader.UnableToLoad:
#                    pass
#            
#            if first_spec is None:
#                return
#            
#            spectrometer = self.spectrometer_manager.get_spectrometer(first_spec.spectrometer_id)
#              
#            self.spectrometer_id_txt.Enable()
#            self.spectrometer_id_txt.SetLabel("Spectrometer ID: %s" %spectrometer.name)
#            
#            self.start_time_txt.Enable()
#            self.start_time_txt.SetLabel(first_spec.capture_time.strftime("Start Time: %H:%M:%S"))
#            
#            last_spec_index = len(spec_files)
#            for f in reversed(spec_files[first_spec_index:]):
#                try:
#                    last_spec = spec_loader.load(f)
#                    last_spec_index -= 1
#                    break
#                except spectrum_loader.UnableToLoad:
#                    pass
#            
#            self.num_of_spectra_txt.Enable()
#            self.num_of_spectra_txt.SetLabel("Number of spectra: %d" %(last_spec_index - first_spec_index))
#            
#            try:
#                self.inband_box.SetValue(spectrometer.get_value("inband_wavelength"))
#            except KeyError:
#                pass
#            
#            try:
#                self.outband_box.SetValue(spectrometer.get_value("outband_wavelength"))
#            except KeyError:
#                pass
#            
#            if last_spec is None:
#                return
#            
#            self.end_time_txt.Enable()
#            self.end_time_txt.SetLabel(last_spec.capture_time.strftime("Start Time: %H:%M:%S"))            
#
#            #TODO - if the user changes the spectrometer properties - save the changes.
#        finally:
#            wx.EndBusyCursor()
#    
#
#class TimePlot(PlotPanelBase):
#    
#    def __init__(self, parent, dir_name, inband, outband, recursive):
#        self.dir_name = dir_name
#        self.inband = inband
#        self.outband = outband
#        self.recursive = recursive
#        self._spec_iter = None
#        self._stay_alive = True
#        
#        #self._create_plot is called by the PlotPanelBase constructor in a new thread
#        PlotPanelBase.__init__(self,parent)
#    
#    
#    def close(self):
#        self._stay_alive = False
#        while self._spec_iter is None:
#            #this could be true if the close event is handled between the 
#            #plot constructor being called and the plotting thread creating
#            #the iterator object
#            time.sleep(0.001)
#            
#        self._spec_iter.close()
#        PlotPanelBase.close(self)
#            
#  
#    def _create_plot(self):
#        ratios = []
#        ratio_calc = spectrum_maths.WavelengthRatioCalc(self.outband, self.inband)
#        matplotlib.interactive(True)
#        l, = self.axes.plot([])
#        
#        i = 0
#        j = 0
#        self._spec_iter = spectra_dir.DarkSubtractedSpectra(self.dir_name, recursive=self.recursive)
#        for s in self._spec_iter:
#            
#            ratios.append(ratio_calc.get_ratio(s))
#            if i > 30:
#                i = 0
#                l.set_data(range(j),ratios[:j])
#                l.axes.relim()
#                if not self._is_zoomed and not self._is_panned:
#                    l.axes.autoscale_view()
#                self.draw_plot()
#            i+=1
#            j+=1
#        
#        if self._stay_alive:
#            l.set_data(range(len(ratios)),ratios)
#            l.axes.relim()
#            
#            if not self._is_zoomed and not self._is_panned:
#                    l.axes.autoscale_view()
#            self.draw_plot()
#        
#        
#class RealtimeTimePlot(TimePlot):
#    
#    def _create_plot(self):
#        ratios = []
#        ratio_calc = spectrum_maths.WavelengthRatioCalc(self.outband, self.inband)
#        matplotlib.interactive(True)
#        l, = self.axes.plot([])
#        #TODO - implement plot updates as a timer in a separate thread
#        t = datetime.datetime.now()
#        j = 0
#        self._spec_iter = spectra_dir.DarkSubtractedSpectra(self.dir_name, recursive=self.recursive, realtime=True)
#        for s in self._spec_iter:
#            ratios.append(ratio_calc.get_ratio(s))
#            if datetime.datetime.now() - t > datetime.timedelta(seconds=1):
#                t = datetime.datetime.now()
#                l.set_data(range(j),ratios[:j])
#                l.axes.relim()
#
#                if not self._is_zoomed and not self._is_panned:
#                    l.axes.autoscale_view()
#                self.draw_plot()
#            
#            j+=1
#        
#        #remember that you never reach here until you close the spec_iter
#        if self._stay_alive:
#            l.set_data(range(len(ratios)),ratios)
#            l.axes.relim()
#            
#            if not self._is_zoomed and not self._is_panned:
#                    l.axes.autoscale_view()
#            self.draw_plot()
#
#
#class RealtimeTimePlotSettingsFrame(TimePlotSettingsFrame):
#    #TODO - implement the extra controls on a realtime plot
#    
#    def get_plot(self):
#        if None in (self.recursive, self.inband, self.outband, self.name):
#            raise RuntimeError("get_plot called before values have been set")
#        return RealtimeTimePlot(self.parent, self.spec_dir, self.inband, self.outband, self.recursive)
# 
        