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

import wx
import os
import threading
import matplotlib
import datetime
import time

from doas.spectrum_loader import SpectrumIO
from doas import spectra_dir
from doas import spectrum_loader
from doas import spectrum_maths

from avoplot.persist import PersistentStorage
from avoplot.gui.plots import PlotPanelBase
from avoplot.plugins import AvoPlotPluginBase
from spectrometers import SpectrometerManager

from std_ops.os_ import find_files


plugin_is_GPL_compatible = True

class TimePlotSettingsFrame(wx.Dialog):
    def __init__(self,parent, name="Time plot settings"):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, name)
        
        self.parent = parent
        self.persist = PersistentStorage()
        self.spectrometer_manager = SpectrometerManager()
        self.spectrometer = None
        
        self.spec_dir = None
        self.recursive = None
        self.inband = None
        self.outband = None
        self.name = "Time plot"
                
        top_panel = wx.Panel(self, wx.ID_ANY)
        self.vsizer = wx.BoxSizer(wx.VERTICAL)
        
        #add the directory browsing box/button
        dirname_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.browse_button = wx.Button(top_panel, wx.ID_ANY, "Browse")
        #make filename box the same height as the button
        self.dir_box = wx.TextCtrl(top_panel, wx.ID_ANY, size=(300,self.browse_button.GetSize()[1]))
        dirname_sizer.Add(self.dir_box, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL)
        dirname_sizer.Add(self.browse_button, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        
        self.vsizer.Add(wx.StaticText(top_panel, wx.ID_ANY, "Spectrum directory:"), 0,wx.LEFT| wx.RIGHT| wx.TOP | wx.ALIGN_TOP, border=10)
        self.vsizer.Add(dirname_sizer, 0, wx.LEFT| wx.RIGHT|wx.ALIGN_CENTER_HORIZONTAL| wx.EXPAND | wx.ALIGN_TOP, border=10)
        
        #add the recursive selection checkbox
        self.recursive_check_box = wx.CheckBox(top_panel, wx.ID_ANY, "Search directory recursively")      
        self.vsizer.Add(self.recursive_check_box,1, wx.ALL|wx.ALIGN_LEFT, border=10)
        
        #add a realtime checkbox
        self.realtime_check_box = wx.CheckBox(top_panel, wx.ID_ANY, "Watch directory for new files")      
        self.realtime_check_box.SetValue(True)
        self.vsizer.Add(self.realtime_check_box,1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ALIGN_LEFT, border=10)
       
        #add spectra info text fields
        self.spectrometer_id_txt = wx.StaticText(top_panel, wx.ID_ANY, "Spectrometer ID:")
        self.num_of_spectra_txt = wx.StaticText(top_panel, wx.ID_ANY, "Number of spectra:")
        self.start_time_txt = wx.StaticText(top_panel, wx.ID_ANY, "Start Time:")
        self.end_time_txt = wx.StaticText(top_panel, wx.ID_ANY, "End Time:")
        
        self.vsizer.AddSpacer(10)
        self.vsizer.Add(self.spectrometer_id_txt,0,wx.ALIGN_LEFT|wx.LEFT, border=10)
        self.vsizer.Add(self.num_of_spectra_txt,0,wx.ALIGN_LEFT|wx.LEFT, border=10)
        self.vsizer.Add(self.start_time_txt,0,wx.ALIGN_LEFT|wx.LEFT, border=10)
        self.vsizer.Add(self.end_time_txt,0,wx.ALIGN_LEFT|wx.LEFT, border=10)
        self.spectrometer_id_txt.Disable()
        self.num_of_spectra_txt.Disable()
        self.start_time_txt.Disable()
        self.end_time_txt.Disable()
        self.vsizer.AddSpacer(10)
        
        #add the inband wavelength selection
        inband_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.inband_box = wx.TextCtrl(top_panel, wx.ID_ANY)
        inband_sizer.Add(wx.StaticText(top_panel, wx.ID_ANY, "Wavelength within SO2 band:"),0,wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        inband_sizer.AddSpacer(5)
        inband_sizer.Add(self.inband_box, 0, wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, border=10)
        self.vsizer.Add(inband_sizer,1,wx.ALIGN_RIGHT)
               
        #add the outband wavelength selection
        outband_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.outband_box = wx.TextCtrl(top_panel, wx.ID_ANY)
        outband_sizer.Add(wx.StaticText(top_panel, wx.ID_ANY, "Wavelength outside SO2 band:"),0,wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        outband_sizer.AddSpacer(5)
        outband_sizer.Add(self.outband_box, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, border=10)
        self.vsizer.Add(outband_sizer,1,wx.ALIGN_RIGHT)  
        
        #add the ok and cancel buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ok_button = wx.Button(top_panel, wx.ID_ANY, "Ok")
        self.cancel_button = wx.Button(top_panel, wx.ID_ANY, "Cancel")
        
        button_sizer.Add(self.cancel_button, 0, wx.ALIGN_RIGHT| wx.ALIGN_BOTTOM)
        button_sizer.Add(self.ok_button, 0, wx.ALIGN_RIGHT| wx.ALIGN_BOTTOM)
        self.vsizer.Add(button_sizer, 1, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT| wx.ALL, border=10)   
        
        top_panel.SetSizer(self.vsizer)      
        top_panel.SetAutoLayout(1)
        self.vsizer.Fit(self)
        
        wx.EVT_BUTTON(self, self.browse_button.GetId(),self.onBrowse)
        wx.EVT_BUTTON(self, self.ok_button.GetId(),self.onOK)
        wx.EVT_BUTTON(self, self.cancel_button.GetId(),self.onCancel)
        wx.EVT_CLOSE(self, self.onCancel)
        self.CenterOnScreen()
        
        
    def get_plot(self):
        if None in (self.recursive, self.inband, self.outband, self.name):
            raise RuntimeError("get_plot called before values have been set")
        
        if self.realtime_check_box.GetValue():
            return RealtimeRatioTimePlot(self.parent, self.spec_dir, self.inband, self.outband, self.recursive)
        else:
            return RatioTimePlot(self.parent, self.spec_dir, self.inband, self.outband, self.recursive)
    
    
    def get_name(self):
        return self.name
    
    
    def onOK(self,evnt):
        self.recursive = self.recursive_check_box.IsChecked()
        self.spec_dir = self.dir_box.GetValue()
        if self.spec_dir == "":
            self.spec_dir = None
            invalid_user_input("No spectrum directory specified.")
            return
        if not os.path.isdir(self.spec_dir):
            invalid_user_input("Cannot open \""+self.spec_dir+"\". No such directory.")
            self.spec_dir = None
            return
        
        self.inband = self.inband_box.GetValue()
        if self.inband == "":
            self.inband = None
            invalid_user_input("No in-band wavelength specified.")
            return

        try:
            self.inband = float(self.inband)
        except ValueError:
            self.inband = None
            invalid_user_input("Invalid value for in-band wavelength.")
            return
        
        self.outband = self.outband_box.GetValue()
        if self.outband == "":
            self.outband = None
            invalid_user_input("No out of band wavelength specified.")
            return

        try:
            self.outband = float(self.outband)
        except ValueError:
            self.outband = None
            invalid_user_input("Invalid value for out of band wavelength.")
            return
        
        #if the spectrometer settings have been changed - then see if the user wants to save them
        if self.spectrometer is not None:
            
            try:
                prev_inband = float(self.spectrometer.get_value("inband_wavelength"))
            except KeyError:
                prev_inband = None
            
            try:
                prev_outband = float(self.spectrometer.get_value("outband_wavelength"))
            except KeyError:
                prev_outband = None
            
            if (prev_inband != self.inband) or (prev_outband != self.outband):
                dialog = wx.MessageDialog(self, "Save these values for the spectrometer %s?"%self.spectrometer.name, style=wx.YES_NO)
                
                if dialog.ShowModal() == wx.ID_YES:
                    self.spectrometer.set_value("inband_wavelength", str(self.inband))
                    self.spectrometer.set_value("outband_wavelength", str(self.outband))
                    self.spectrometer_manager.update(self.spectrometer)
        
        
        self.EndModal(wx.OK)
        self.Destroy()

    
    def onCancel(self, evnt):
        self.EndModal(wx.CANCEL)
        self.Destroy()

    
    def onBrowse(self, evnt):
        try:
            last_path_used = self.persist.get_value("spectra_dir")
            #want the parent directory of the spec_dir
            last_path_used = os.path.join(last_path_used, os.path.pardir)
        except KeyError:
            last_path_used = ""
        
        spec_dir = wx.DirSelector("Choose spectrum directory", defaultPath=last_path_used)

        if spec_dir == "":
            return
        
        #set the name to the directory name
        self.name = os.path.basename(spec_dir)
        
        wx.BeginBusyCursor()
        wx.Yield()
        try:
            self.persist.set_value("spectra_dir", spec_dir)
            self.dir_box.SetValue(spec_dir)
            
            if self.recursive_check_box.IsChecked():
                spec_files = find_files(spec_dir, recursive=True)
            else:
                spec_files = [os.path.join(spec_dir, n) for n in os.listdir(spec_dir)]
            
            spec_loader = spectrum_loader.SpectrumIO()
            first_spec = None
            last_spec = None
            first_spec_index = 0
            for f in spec_files:
                try:
                    first_spec = spec_loader.load(f)
                    first_spec_index += 1
                    break
                except spectrum_loader.UnableToLoad:
                    pass
            
            if first_spec is None:
                return
            
            self.spectrometer = self.spectrometer_manager.get_spectrometer(first_spec.spectrometer_id)
              
            self.spectrometer_id_txt.Enable()
            self.spectrometer_id_txt.SetLabel("Spectrometer ID: %s" %self.spectrometer.name)
            
            self.start_time_txt.Enable()
            self.start_time_txt.SetLabel(first_spec.capture_time.strftime("Start Time: %H:%M:%S"))
            
            last_spec_index = len(spec_files)
            for f in reversed(spec_files[first_spec_index:]):
                try:
                    last_spec = spec_loader.load(f)
                    last_spec_index -= 1
                    break
                except spectrum_loader.UnableToLoad:
                    pass
            
            self.num_of_spectra_txt.Enable()
            self.num_of_spectra_txt.SetLabel("Number of spectra: %d" %(last_spec_index - first_spec_index))
            
            try:
                self.inband_box.SetValue(self.spectrometer.get_value("inband_wavelength"))
            except KeyError:
                pass
            
            try:
                self.outband_box.SetValue(self.spectrometer.get_value("outband_wavelength"))
            except KeyError:
                pass
            
            if last_spec is None:
                return
            
            self.end_time_txt.Enable()
            self.end_time_txt.SetLabel(last_spec.capture_time.strftime("End Time: %H:%M:%S"))            

            #TODO - if the user changes the spectrometer properties - save the changes.
        finally:
            wx.EndBusyCursor()
 

class RatioTimePlot(PlotPanelBase):
    
    def __init__(self, parent, dir_name, inband, outband, recursive):
        self.dir_name = dir_name
        self.inband = inband
        self.outband = outband
        self.recursive = recursive
        self._spec_iter = None
        self._stay_alive = True
        self._found_dark_lock = threading.Lock()
        self._found_dark_lock.acquire() #lock is released when dark spectrum is found
        
        PlotPanelBase.__init__(self,parent,os.path.basename(dir_name))
        
        self.plotting_thread = threading.Thread(target=self._create_plot)
        self.plotting_thread.start()
    
    
    def wait_for_dark(self):
        """
        Blocks until a dark spectrum is found.
        """
        self._found_dark_lock.acquire()
        self._found_dark_lock.release()
        print "exited wait_for_dark"
    
    
    def close(self):
        self._stay_alive = False
        while self._spec_iter is None:
            #this could be true if the close event is handled between the 
            #plot constructor being called and the plotting thread creating
            #the iterator object
            time.sleep(0.001)
            
        self._spec_iter.close()
        if self._found_dark_lock.locked():
                self._found_dark_lock.release()
        self.plotting_thread.join()
        PlotPanelBase.close(self)
        
    
    def draw_plot(self):
        try:
            wx.MutexGuiEnter()
            self.canvas.draw()
            self.canvas.gui_repaint()
        finally:
            wx.MutexGuiLeave()
    
    
    def set_dark_spectra(self, spectra):
        loader = spectrum_loader.SpectrumIO()
        
        spectra_objs = [loader.load(f) for f in spectra]
        spectra_objs = [s for s in spectra_objs if s is not None]
        if self._spec_iter is not None:
            print spectra_objs
            self._spec_iter.set_dark_spectra(spectra_objs)
            print "finished calling self._spec_iter.set_dark_spectra"
        else:
            #TODO - handle this properly
            raise RuntimeError("Call to set_darks before iterator is initialised")
    
    
    def _create_plot(self):
        ratios = []
        ratio_calc = spectrum_maths.WavelengthRatioCalc(self.outband, self.inband)
        matplotlib.interactive(True)
        l, = self.axes.plot([])
        
        i = 0
        j = 0
        self._spec_iter = spectra_dir.DarkSubtractedSpectra(self.dir_name, recursive=self.recursive)
        for s in self._spec_iter:
            if self._found_dark_lock.locked():
                print "_create_plot released lock"
                self._found_dark_lock.release()
                
            ratios.append(ratio_calc.get_ratio(s))
            if i > 30:
                i = 0
                l.set_data(range(j),ratios[:j])
                l.axes.relim()
                if not self._is_zoomed and not self._is_panned:
                    l.axes.autoscale_view()
                self.draw_plot()
            i+=1
            j+=1
        
        if self._stay_alive:
            l.set_data(range(len(ratios)),ratios)
            l.axes.relim()
            
            if not self._is_zoomed and not self._is_panned:
                    l.axes.autoscale_view()
            self.draw_plot()
 
 
            
class RealtimeRatioTimePlot(RatioTimePlot):
    
    def _create_plot(self):
        ratios = []
        ratio_calc = spectrum_maths.WavelengthRatioCalc(self.outband, self.inband)
        matplotlib.interactive(True)
        l, = self.axes.plot([])
        #TODO - implement plot updates as a timer in a separate thread
        t = datetime.datetime.now()
        j = 0
        self._spec_iter = spectra_dir.DarkSubtractedSpectra(self.dir_name, recursive=self.recursive, realtime=True)
        for s in self._spec_iter:
            if self._found_dark_lock.locked():
                print "_create_plot released lock"
                self._found_dark_lock.release()
            
            ratios.append(ratio_calc.get_ratio(s))
            if datetime.datetime.now() - t > datetime.timedelta(seconds=1):
                t = datetime.datetime.now()
                l.set_data(range(j),ratios[:j])
                l.axes.relim()

                if not self._is_zoomed and not self._is_panned:
                    l.axes.autoscale_view()
                self.draw_plot()
            
            j+=1
        
        #remember that you never reach here until you close the spec_iter
        if self._stay_alive:
            l.set_data(range(len(ratios)),ratios)
            l.axes.relim()
            
            if not self._is_zoomed and not self._is_panned:
                    l.axes.autoscale_view()
            self.draw_plot()            

class DarkSelectDialog(wx.Dialog):
    def __init__(self, plot_obj):
        self._wait_for_dark_thread = threading.Thread(target=self.__wait_for_dark)
        self.plot_obj = plot_obj
        wx.Dialog.__init__(self,plot_obj, wx.ID_ANY)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        
        vsizer.Add(wx.StaticText(self, wx.ID_ANY, "Waiting for dark spectrum..."),0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, border=10)
        
        self.manual_select_button = wx.Button(self, wx.ID_ANY, "Select manually")
        vsizer.Add( self.manual_select_button, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, border=10)   
        self._wait_for_dark_thread.start()
        
        self.SetSizer(vsizer)
        vsizer.Fit(self)
        self.SetAutoLayout(True)
        
        wx.EVT_BUTTON(self, self.manual_select_button.GetId(), self.onSelect)
        wx.EVT_CLOSE(self, self.onClose)
    
    def onClose(self, evnt):
        #TODO - this should probably close the plot as well - difficult since it is handled 
        #by a notebook
        self.plot_obj.close()
        self._wait_for_dark_thread.join()
        self.Destroy()
    
    
    def onSelect(self, evnt):
        persist = PersistentStorage()
        try:
            default_dir = persist.get_value("spectra_dir")
            default_dir = os.path.join(default_dir, os.path.pardir)
        except KeyError:
            default_dir =""
        
        dialog = wx.FileDialog(self, "Choose dark spectrum file(s)", defaultDir=default_dir,style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST|wx.FD_MULTIPLE)
        if dialog.ShowModal() == wx.ID_OK:
            darks = dialog.GetPaths()
            self.plot_obj.set_dark_spectra(darks)

    
    def __wait_for_dark(self):
        self.plot_obj.wait_for_dark()
        while not self.IsModal():
            time.sleep(0.01)
        print "DarkSelectDialog - finished waiting for dark"
        wx.CallAfter(self.EndModal,wx.ID_OK)
        #self.EndModal(wx.ID_OK)
            
            
class RatioTimePlugin(AvoPlotPluginBase):
    
    def __init__(self):
        AvoPlotPluginBase.__init__(self, "DOAS Ratio time series")
    
    
    def get_onNew_handler(self):
        return ("DOAS", "Ratio Time Plot", "Plot time series of ratios", self.plot_ratio_timeseries)
    
    
    def plot_ratio_timeseries(self, evnt):
        # TODO - open a time plot and select the zoom tool while it is plotting.
        # now open a second time plot (the zoom tool is disabled), but if you switch
        # back to the first time plot once it has finished plotting, then the axes are
        # not autoscaled. This is not a major issue, but should be fixed.
        parent = self.get_parent()
        dialog = TimePlotSettingsFrame(parent)
        if (dialog.ShowModal() == wx.OK):
            time_plot = dialog.get_plot()
            
            if parent.toolbar.GetToolState(parent.toolbar.zoom_tool.GetId()):
                #then diasble the zoom (so that the plot gets autoscaled as data is added)
                parent.toolbar.ToggleTool(parent.toolbar.zoom_tool.GetId(), False)
                
            elif parent.toolbar.GetToolState(parent.toolbar.move_tool.GetId()):
                #then disable the panning (again so that the plot gets autoscaled as data is added)
                parent.toolbar.ToggleTool(parent.toolbar.move_tool.GetId(), False)
            
            self.add_plot_to_main_window(time_plot)
            
            wx.CallAfter(self.create_manual_dark_select_frame, time_plot)
    
    
    def create_manual_dark_select_frame(self, plot_obj):
        dialog = DarkSelectDialog(plot_obj)
        dialog.ShowModal()
        
           
