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
The main module contains the code for the main frame of the AvoPlot GUI. 
"""

import wx
from wx import aui
from matplotlib.backends import backend_wx
import sys
import os
import warnings

import avoplot
from avoplot import core
from avoplot.gui import menu
from avoplot.gui import toolbar
from avoplot.gui import plots_panel
from avoplot.gui import control_panel
from avoplot.gui import nav_panel
from avoplot.gui import artwork
from avoplot import persist
import avoplot.plugins



class MainFrame(wx.Frame):
    """
    Main frame of the GUI. This is set as the top level window when the 
    AvoPlot App is created in the AvoPlot.py script.
    """   
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, avoplot.PROG_SHORT_NAME)
    
    def launch(self, start_hidden=False):
        """
        Create all the GUI elements and show the main window. Note that this 
        needs to be separate from the __init__ method, since we need set the top
        level window for wx before calling launch().
        """
        #create the persistent settings object
        self.persistant = persist.PersistentStorage()
        
        #create a new session to hold all the figures
        self.session = core.AvoPlotSession('/')
        
        #set up the icon for the frame
        if sys.platform == "win32":
            self.SetIcon(wx.ArtProvider.GetIcon("avoplot", size=(16,16)))
        else:
            self.SetIcon(wx.ArtProvider.GetIcon("avoplot", size=(64,64)))
        
        #create main GUI panels
        self.plots_panel = plots_panel.PlotsPanel(self)
        self.ctrl_panel = control_panel.ControlPanel(self)
        self.nav_panel = nav_panel.NavigationPanel(self, self.session)
        
        #create the menus
        self.menu = menu.MainMenu(self)
        self.SetMenuBar(self.menu)
        
        #create the toolbar
        self.toolbar = toolbar.MainToolbar(self)
        self.SetToolBar(self.toolbar)
        
        #create the manager to deal with the various panels
        self._mgr = aui.AuiManager(self)
              
        #create the status bar
        self.statbar = backend_wx.StatusBarWx(self) 
        self.SetStatusBar(self.statbar)
        
        #put the various panes into the manager
        self._mgr.AddPane(self.ctrl_panel, aui.AuiPaneInfo().Bottom().Left().Caption('Control Panel').Name('ctrl_panel'))
        self._mgr.AddPane(self.nav_panel, aui.AuiPaneInfo().Top().Left().Caption('Navigation Panel').Name('nav_panel'))
        self._mgr.AddPane(self.plots_panel, aui.AuiPaneInfo().Center().Name('plt_panel').CloseButton(False).CaptionVisible(False).Floatable(False).Dockable(False))
        
        #try to load the last manager setup
        try:
            state = self.persistant.get_value('manager_state')
            self._mgr.LoadPerspective(state, update=False)
        except KeyError:
            pass
        
        #default to showing all the panes
        for p in self._mgr.GetAllPanes():
            p.Show(True)
        
        self._mgr.Update()

        #register the event handlers
        self.Bind(core.EVT_AVOPLOT_ELEM_SELECT, self.on_avoplot_event)
        self.Bind(core.EVT_AVOPLOT_ELEM_ADD, self.on_avoplot_event)
        self.Bind(core.EVT_AVOPLOT_ELEM_RENAME, self.on_avoplot_event)
        self.Bind(core.EVT_AVOPLOT_ELEM_DELETE, self.on_avoplot_event)
        
        menu.EVT_AVOPLOT_CTRL_PANEL_STATE(self, self.on_show_ctrl_panel)
        menu.EVT_AVOPLOT_NAV_PANEL_STATE(self, self.on_show_nav_panel)  
                    
        aui.EVT_AUI_PANE_CLOSE(self, self.on_pane_close)

        wx.EVT_CLOSE(self, self.on_close)

        
        #see what size the frame was in the last session
        try:
            old_size = self.persistant.get_value('main_frame_size')            
            min_size = wx.Size(500,500) #don't restore the old size if it is too small
            
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
        
        if not start_hidden:
            self.Show()
    
    
    def on_pane_close(self, evnt):
        """
        Event handler for pane close events (where the panes are those managed
        by the AUI manager of the MainFrame object - currently just the control
        pane and the navigation pane).
        """
        p = evnt.GetPane()
        if p.caption == "Control Panel":
            evt = menu.AvoPlotCtrlPanelChangeState(state=False)
            wx.PostEvent(self.menu, evt)
        elif p.caption == "Navigation Panel":
            evt = menu.AvoPlotNavPanelChangeState(state=False)
            wx.PostEvent(self.menu, evt)
    
    
    def on_show_ctrl_panel(self, evnt):
        """
        Event handler for the "unhiding" of the control pane.
        """
        p = self._mgr.GetPane(self.ctrl_panel)    
        p.Show(evnt.state)
        self.ctrl_panel.reset_control_panels()
        self._mgr.Update()
        
        
        
    def on_show_nav_panel(self, evnt):
        """
        Event handler for the "unhiding" of the navigation pane.
        """       
        p = self._mgr.GetPane(self.nav_panel)    
        p.Show(evnt.state)
        self._mgr.Update()
    
    
    def on_avoplot_event(self, evnt):
        """
        All AvoPlot events (see the 'core' module) are posted to the MainFrame
        where they are handled by this method. All it does is to repost the 
        event to all the GUI components so that they can react as needed.
        """
        #pass the event on to all the GUI elements
        wx.PostEvent(self.nav_panel, evnt)
        wx.PostEvent(self.ctrl_panel, evnt)
        wx.PostEvent(self.menu, evnt)
        wx.PostEvent(self.toolbar, evnt)
        
        #this has to come last since fig.Destroy() will get called inside the
        # plots panel event handler and
        #so subsequent access to fig will raise an exception
        wx.PostEvent(self.plots_panel, evnt) 
   

        
    def on_close(self, *args):
        """
        Handler called when the MainFrame is closed. This performs all the tidy
        up operations such as saving program state. Note that all elements that
        can be reached through the AvoPlotSession - i.e. all those that have a 
        parent that isn't None, will have their delete() method called before 
        the program exits.
        """
        #unregister handlers for selection changed events to prevent on_select
        #handlers from attempting to access destroyed frames
        self.Unbind(core.EVT_AVOPLOT_ELEM_SELECT)
        
        self.session.delete()
        
        #save the final size of the frame so that it can be loaded next time
        self.persistant.set_value('main_frame_maximised', self.IsMaximized())
        
        if not self.IsMaximized():
            self.persistant.set_value('main_frame_size', self.GetSizeTuple())
        
        #save the state of the manager so that the panels will restore to 
        #the same size etc.
        self.persistant.set_value('manager_state', self._mgr.SavePerspective())
        
        self._mgr.UnInit()

        self.Destroy()
        
        
    def add_figure(self, figure):
        """
        Adds a figure element (an avoplot.figure.AvoPlotFigureBase instance) to 
        the current session.
        """
        figure.finalise(self)
        figure.set_status_bar(self.statbar)
        figure.set_parent_element(self.session)
        figure.set_selected()



def display_warning(message, category, filename, *args):
    """
    Displays a warning message in a wx.MessageBox. This is designed to 
    override the warnings module's show_warning function.
    """
    wx.MessageBox(str(message), avoplot.PROG_SHORT_NAME, wx.ICON_ERROR)



class AvoPlotApp(wx.App):
    """
    wx app for the AvoPlot program. Overrides the OnInit method to do some 
    startup tasks.
    """
    def __init__(self, options, args, start_hidden=False):
        self.options = options
        self.args = args
        self.start_hidden = start_hidden
        self.main_frame = None
        
        super(AvoPlotApp, self).__init__()
        
        self.Bind(wx.EVT_IDLE, self.on_idle)
    
    
    def on_idle(self, evnt):
        while avoplot.call_on_idle.idle_q:
            f, args, kwargs = avoplot.call_on_idle.idle_q.popleft()
            f(*args, **kwargs)
    
    
    def MainLoop(self):

        super(AvoPlotApp, self).MainLoop()
        
        #execute any pending on_idle events.
        self.on_idle(None)
    
    
    def OnInit(self):
        #setup warnings module to display messages in a wx.MessageBox
        warnings.showwarning = display_warning
        
        #register our art provider to serve the AvoPlot icons
        wx.ArtProvider.Insert(artwork.AvoplotArtProvider())
        
        #load all available plugins
        avoplot.plugins.load_all_plugins()
        
        #launch the GUI!
        self.main_frame = MainFrame()
        self.SetTopWindow(self.main_frame)
        self.main_frame.launch(start_hidden=self.start_hidden)
        
        return True
  
