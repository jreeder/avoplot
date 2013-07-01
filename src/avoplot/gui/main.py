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
from wx import aui
from matplotlib.backends import backend_wx

import avoplot
from avoplot import core
from avoplot.gui import menu
from avoplot.gui import toolbar
from avoplot.gui import plots_panel
from avoplot.gui import control_panel
from avoplot.gui import nav_panel
from avoplot import persist


class AvoPlotSession(core.AvoPlotElementBase):
    pass


class MainFrame(wx.Frame):      
    def __init__(self):
        #create the persistent settings object
        self.persistant = persist.PersistentStorage()
        
        #create a new session to hold all the figures
        self.session = AvoPlotSession('/')
        
        wx.Frame.__init__(self, None, wx.ID_ANY, avoplot.PROG_SHORT_NAME)
        
        #set up the icon for the frame
        self.SetIcon(wx.ArtProvider.GetIcon("avoplot"))
        
        #create main GUI panels
        self.plots_panel = plots_panel.PlotsPanel(self)
        self.ctrl_panel = control_panel.ControlPanel(self)
        self.nav_panel = nav_panel.NavigationPanel(self, self.session)
        
        #create the menus
        self.menu = menu.MainMenu(self)
        self.SetMenuBar(menu.MainMenu(self))
        
        #create the toolbar
        self.toolbar = toolbar.MainToolbar(self)
        self.SetToolBar(self.toolbar)
        
        #create the manager to deal with the various panels
        self._mgr = aui.AuiManager(self)
              
        #create the status bar
        self.statbar = backend_wx.StatusBarWx(self) 
        self.SetStatusBar(self.statbar)
        
        #put the various panes into the manager
        #TODO - update visibility based on persistent setting
        #TODO - need to update menu if panel is closed.
        self._mgr.AddPane(self.ctrl_panel, wx.LEFT, 'Control Panel')
        self._mgr.AddPane(self.nav_panel, wx.LEFT | wx.TOP, 'Navigation Panel')
        self._mgr.AddPane(self.plots_panel, wx.CENTER)
        
        self._mgr.Update()

        #register the event handlers
        core.EVT_AVOPLOT_ELEM_SELECT(self, self.on_avoplot_event)
        core.EVT_AVOPLOT_ELEM_ADD(self, self.on_avoplot_event)
        core.EVT_AVOPLOT_ELEM_DELETE(self, self.on_avoplot_event)
        core.EVT_AVOPLOT_ELEM_RENAME(self, self.on_avoplot_event)
                       
        wx.EVT_CLOSE(self, self.on_close)

        
        #see what size the frame was in the last session
        try:
            old_size = self.persistant.get_value('main_frame_size')            
            min_size = wx.Size(500,500) #TODO - come up with a good val for this
            
            size = (max(min_size[0], old_size[0]), 
                    max(min_size[1], old_size[1]))
            self.SetSize(size)

        except KeyError:
            pass
        
        #see if the frame was maximised last time
        try:
            maximised = self.persistant.get_value('main_frame_maximised')
            self.Maximize(maximised)
        except KeyError:
            pass
        
        self.Show()
    
    
    def show_ctrl_panel(self, val):
        """
        if val is True then shows the control panel, otherwise hides it
        """
        p = self._mgr.GetPane(self.ctrl_panel)    
        p.Show(val)
        self._mgr.Update()
        
        
    def show_nav_panel(self, val):
        """
        if val is True then shows the navigation panel, otherwise hides it
        """
        p = self._mgr.GetPane(self.nav_panel)    
        p.Show(val)
        self._mgr.Update()
    
    
    def on_avoplot_event(self, evnt):
        #pass the event on to all the GUI elements
        wx.PostEvent(self.nav_panel, evnt)
        wx.PostEvent(self.ctrl_panel, evnt)
        wx.PostEvent(self.menu, evnt)
        wx.PostEvent(self.toolbar, evnt)
        
        #this has to come last since fig.Destroy() will get called here and
        #so subsequent access to fig will raise an exception
        wx.PostEvent(self.plots_panel, evnt) 
   

        
    def on_close(self, *args):
        #TODO - unregister handlers for selection changed events
        
        self.session.delete()
        
        #save the final size of the frame so that it can be loaded next time
        self.persistant.set_value('main_frame_maximised', self.IsMaximized())
        
        if not self.IsMaximized():
            self.persistant.set_value('main_frame_size', self.GetSize())

        self._mgr.UnInit()

        self.Destroy()
        
        
    def add_figure(self, figure):
        figure.finalise()
        figure.set_status_bar(self.statbar)
        figure.set_parent_element(self.session)
        figure.set_selected()
  
            

        
        
        
        
        
