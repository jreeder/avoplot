#Copyright (C) Nial Peters 2012
#
#This file is part of AvoScan.
#
#AvoScan is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#AvoScan is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with AvoScan.  If not, see <http://www.gnu.org/licenses/>.

import wx
from wx.lib.agw.flatnotebook import FlatNotebook, EVT_FLATNOTEBOOK_PAGE_CHANGED, EVT_FLATNOTEBOOK_PAGE_CLOSED, FNB_FANCY_TABS, FNB_X_ON_TAB,FNB_NO_X_BUTTON, EVT_FLATNOTEBOOK_PAGE_CLOSING
import os.path
from avoplot.gui.artwork import AvoplotArtProvider
from avoplot import spectrometers
from avoplot.gui import menu
from avoplot.gui import toolbar
from avoplot import persist
from avoplot.gui import plots
from doas.spectrum_loader import UnableToLoad


class MainFrame(wx.Frame):      
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "AvoPlot")
        
        #set up the icon for the frame
        art = AvoplotArtProvider()
        wx.ArtProvider.Push(art)
        self.SetIcon(art.GetIcon("AvoPlot"))
        
        #create the persistant settings object
        self.persistant = persist.PersistantStorage()
        
        #create the spectrometer manger object
        self.spectrometer_manager = spectrometers.SpectrometerManager()
        
        #create the menu
        self.menu = menu.MainMenu(self)
        self.SetMenuBar(menu.MainMenu(self))
        
        #create the toolbar
        self.toolbar = toolbar.MainToolbar(self)
        self.SetToolBar(self.toolbar)
        
        #create the notebook
        self.notebook = FlatNotebook(self, id = wx.ID_ANY, style=FNB_FANCY_TABS|FNB_X_ON_TAB|FNB_NO_X_BUTTON)
        
        wx.EVT_CLOSE(self, self.onClose)
        EVT_FLATNOTEBOOK_PAGE_CLOSING(self, self.notebook.GetId(), self.onTabClose)
        EVT_FLATNOTEBOOK_PAGE_CLOSED(self, self.notebook.GetId(), self.onTabChange)
        EVT_FLATNOTEBOOK_PAGE_CHANGED(self, self.notebook.GetId(), self.onTabChange)
        self.Show()
    
    
    def onTabClose(self, evnt):
        p = self.get_active_plot()
        p.close()
        
        
    def onTabChange(self,evnt):
        p = self.get_active_plot()
        if p is None:
            self.toolbar.enable_plot_tools(False)
            return
        
        self.toolbar.enable_plot_tools(True)
        
        #set the zoom settings on the plot based on the toolbar selection
        if self.toolbar.GetToolState(self.toolbar.zoom_tool.GetId()):
            #then zoom tool is selected
            if not p._is_zoomed:
                p.zoom()
        else:
            if p._is_zoomed:
                p.zoom()
        
        if self.toolbar.GetToolState(self.toolbar.move_tool.GetId()):
            #then zoom tool is selected
            if not p._is_panned:
                p.pan()
        else:
            if p._is_panned:
                p.pan()
        
        #set the toolbar gridlines button, based on the plot object
        self.toolbar.ToggleTool(self.toolbar.grid_tool.GetId(), p._gridlines)
    
    
    def get_active_plot(self):
        return self.notebook.GetCurrentPage()

        
    def onClose(self, *args):
        #close each plot in turn in order to shut down the plotting threads
        for i in range(0,self.notebook.GetPageCount(),):
            self.notebook.GetPage(i).close()
        self.Destroy()

    
    def onSpectrumPlot(self,*args):
        
        try:
            last_path_used = self.persistant.get_value("spectra_dir")
        except KeyError:
            last_path_used = ""
        
        #get filename to open
        spectrum_file = wx.FileSelector("Choose spectrum file to open", default_path=last_path_used)
        if spectrum_file == "":
            return
        
        self.persistant.set_value("spectra_dir", os.path.dirname(spectrum_file))
        
        try:
            spec_plot = plots.SpectrumPlot(self, spectrum_file)
        except UnableToLoad:
            wx.MessageBox("Unable to load spectrum. Unrecognised file format.", "AvoPlot", wx.ICON_ERROR)
            return
        
        self.notebook.AddPage(spec_plot,os.path.basename(spectrum_file), select=True)
        

    def onTimePlot(self,*args):
        
        # TODO - open a time plot and select the zoom tool while it is plotting.
        # now open a second time plot (the zoom tool is disabled), but if you switch
        # back to the first time plot once it has finished plotting, then the axes are
        # not autoscaled. This is not a major issue, but should be fixed.
        
        dialog = plots.TimePlotSettingsFrame(self, self.persistant, self.spectrometer_manager)
        if (dialog.ShowModal() == wx.OK):
            time_plot = dialog.get_plot()
            
            if self.toolbar.GetToolState(self.toolbar.zoom_tool.GetId()):
                #then diasble the zoom (so that the plot gets autoscaled as data is added)
                self.toolbar.ToggleTool(self.toolbar.zoom_tool.GetId(), False)
                
            elif self.toolbar.GetToolState(self.toolbar.move_tool.GetId()):
                #then disable the panning (again so that the plot gets autoscaled as data is added)
                self.toolbar.ToggleTool(self.toolbar.move_tool.GetId(), False)
                
            self.notebook.AddPage(time_plot,dialog.get_name(), select=True)
        
    
    def onRealtimeTimePlot(self,*args):
        
        dialog = plots.RealtimeTimePlotSettingsFrame(self, self.persistant, self.spectrometer_manager, name="Realtime time plot settings")
        if (dialog.ShowModal() == wx.OK):
            time_plot = dialog.get_plot()
            
            if self.toolbar.GetToolState(self.toolbar.zoom_tool.GetId()):
                #then diasble the zoom (so that the plot gets autoscaled as data is added)
                self.toolbar.ToggleTool(self.toolbar.zoom_tool.GetId(), False)
                
            elif self.toolbar.GetToolState(self.toolbar.move_tool.GetId()):
                #then disable the panning (again so that the plot gets autoscaled as data is added)
                self.toolbar.ToggleTool(self.toolbar.move_tool.GetId(), False)
                
            self.notebook.AddPage(time_plot,dialog.get_name(), select=True)
    
    
    def onSavePlot(self, *args):
        self.notebook.GetCurrentPage().save_plot()
        
        
        
        
        
