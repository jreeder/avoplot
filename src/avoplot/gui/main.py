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
import re
import wx
from wx import aui
from matplotlib.backends import backend_wx

import avoplot
from avoplot import core
from avoplot.gui import menu
from avoplot.gui import toolbar
from avoplot.gui import control_panel
from avoplot.gui import navigation
from avoplot import persist



class MainFrame(wx.Frame):      
    def __init__(self):
        #create the persistant settings object
        self.persistant = persist.PersistentStorage()
        
        wx.Frame.__init__(self, None, wx.ID_ANY, avoplot.PROG_SHORT_NAME)
        
        #set up the icon for the frame
        self.SetIcon(wx.ArtProvider.GetIcon("avoplot"))
        
        #create the menus
        self.menu = menu.MainMenu(self)
        self.SetMenuBar(menu.MainMenu(self))
        self._tab_menu = menu.TabRightClickMenu(self)
        
        #create the toolbar
        self.toolbar = toolbar.MainToolbar(self)
        self.SetToolBar(self.toolbar)
        
        vsizer = wx.BoxSizer(wx.VERTICAL)
        
        #create the manager to deal with the various panels
        self._mgr = aui.AuiManager(self)
        
        #create the notebook
        self.notebook = aui.AuiNotebook(self, id=wx.ID_ANY, 
                                        style=aui.AUI_NB_DEFAULT_STYLE)
        
        self.ctrl_panel = control_panel.ControlPanel(self)
        self.nav_panel = navigation.NavigationPanel(self)
               
        #create the status bar
        self.statbar = backend_wx.StatusBarWx(self) 
        self.SetStatusBar(self.statbar)
        
        #put the various panes into the manager
        #TODO - update visibility based on persistent setting
        #TODO - need to update menu if panel is closed.
        self._mgr.AddPane(self.ctrl_panel, wx.LEFT, 'Control Panel')
        self._mgr.AddPane(self.nav_panel, wx.LEFT | wx.TOP, 'Navigation Panel')
        self._mgr.AddPane(self.notebook, wx.CENTER)
        
        self._mgr.Update()

        #register the event handlers
        core.EVT_AVOPLOT_ELEM_CHANGE(self, self.ctrl_panel.on_element_selection)
        wx.EVT_CLOSE(self, self.onClose)
        aui.EVT_AUINOTEBOOK_PAGE_CLOSE(self, self.notebook.GetId(), 
                                       self.onTabClose)
        aui.EVT_AUINOTEBOOK_PAGE_CLOSED(self, self.notebook.GetId(), 
                                        self.onTabChange)
        aui.EVT_AUINOTEBOOK_PAGE_CHANGED(self, self.notebook.GetId(), 
                                         self.onTabChange)
        
        try:
            aui.EVT_AUINOTEBOOK_TAB_RIGHT_DOWN(self, self.notebook.GetId(), 
                                               self.onTabRightClick)
        except AttributeError:
            #new version of wx has renamed this for some reason!
            aui.EVT__AUINOTEBOOK_TAB_RIGHT_DOWN(self, self.notebook.GetId(), 
                                                self.onTabRightClick)
        
        #see what size the frame was in the last session
        try:
            old_size = self.persistant.get_value('main_frame_size')            
            min_size = vsizer.GetMinSize()
            
            size = (max(min_size[0], old_size[0]), 
                    max(min_size[1], old_size[1]))
            self.SetSize(size)

        except KeyError:
            pass
        
        #see if the frame was maximised last time
        try:
            maximised = self.persistant.get_value('main_frame_maximised')
            self.Maximize(maximised)
        except:
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
    
    
    def onTabClose(self, evnt):
        p = self.get_active_plot()
        p.close()
   
        
    def onTabRightClick(self, evnt):
        self.notebook.SetSelection(evnt.GetSelection())
        self.PopupMenu(self._tab_menu)
    
    
    def rename_current_tab(self, evnt):
        page_idx = self.notebook.GetSelection()
        current_name = self.notebook.GetPage(page_idx).name
        
        d = wx.TextEntryDialog(self, "Plot name:", "Rename", 
                               defaultValue=current_name)
        
        if d.ShowModal() == wx.ID_OK:
            new_name = d.GetValue()
            if (new_name and not new_name.isspace() and 
                new_name != current_name):
                self.set_page_name(page_idx, new_name)
            
            
    def onTabChange(self, evnt):
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
        
        p.set_selected()
        
        #TODO- this should be done in the event handler
    
    
    def get_active_plot(self):
        selection = self.notebook.GetSelection()

        if selection == -1:
            #means that no plots are open
            return None
        
        return self.notebook.GetPage(selection)

    
    def get_all_pages(self):
        """
        Returns a list of all the pages currently managed by the notebook.
        """
        return [self.notebook.GetPage(i) for i in range(self.notebook.GetPageCount())]
        
    
    def split_plot_horiz(self, *args):
        self.notebook.Split(self.notebook.GetSelection(), wx.RIGHT)
       
        
    def split_plot_vert(self, *args):
        self.notebook.Split(self.notebook.GetSelection(), wx.BOTTOM)    
        
        
    def unsplit_panes(self, *args):
        self.notebook.Freeze()

        # remember the tab now selected
        nowSelected = self.notebook.GetSelection()
        # select first tab as destination
        self.notebook.SetSelection(0)
        # iterate all other tabs
        for idx in xrange(1, self.notebook.GetPageCount()):
            # get win reference
            win = self.notebook.GetPage(idx)
            # get tab title
            title = self.notebook.GetPageText(idx)
            # get page bitmap
            bmp = self.notebook.GetPageBitmap(idx)
            # remove from notebook
            self.notebook.RemovePage(idx)
            # re-add in the same position so it will tab
            self.notebook.InsertPage(idx, win, title, False, bmp)
        # restore orignial selected tab
        self.notebook.SetSelection(nowSelected)

        self.notebook.Thaw()
       
        #self.notebook.UnSplit()
      
        
    def onClose(self, *args):
        #close each plot in turn - they may have clean-up operations they need
        #to complete
        self.Freeze()
        for i in range(0, self.notebook.GetPageCount(),):
            self.notebook.GetPage(i).close()
        self.Thaw()
        #save the final size of the frame so that it can be loaded next time
        self.persistant.set_value('main_frame_maximised', self.IsMaximized())
        
        if not self.IsMaximized():
            self.persistant.set_value('main_frame_size', self.GetSize())

        self._mgr.UnInit()
        self.Destroy()
   
    
    
    def close_plot(self, idx):
        """
        Closes the plot at the specified index.
        """
        #call the plot's close method
        self.notebook.GetPage(idx).close()
        
        #delete it from the notebook
        self.notebook.DeletePage(idx)
        
        self.onTabChange(None)
        
    
    def add_tab(self, plot, select=True):
        plot.finalise()
        #check if a plot tab with this name already exists       
        name = plot.name
        plot.name = '' #this is a hack to get the naming to work correctly
        self.notebook.AddPage(plot, '', select=select)
        self.set_page_name(self.notebook.GetPageCount() - 1, name)
         
        #allow the plot to talk to the status bar
        plot.set_status_bar(self.statbar)

    
    def set_page_name(self, idx, name):
        """
        Sets the name of the notebook page at the specified index. If a page
        with the same name already exists then a copy number is appended to 
        the specified name. Note that this method will update the value
        of the name attribute of the plot contained in the notebook page - 
        however, the copy number will not be included in the attribute value.
        """
        current_names = [p.name for p in self.get_all_pages()]  
        count = current_names.count(name)
        
        #set the name in the plot object
        self.notebook.GetPage(idx).name = name
        
        if count > 0:
            current_indices = [1]
            #this name is already in use - find what the 
            #highest index of current use is (don't want to go back to
            #lower numbers if some intermediate tab is closed)
            plot_titles = [self.notebook.GetPageText(i) for i in range(self.notebook.GetPageCount())]
            
            for title in plot_titles:
                if not title.startswith(name):
                    continue
                title = title[len(name):].strip()
                
                if title:
                    match = re.match(r'\(([0-9]+)\)', title)
                    if match:
                        current_indices.append(int(match.groups()[0]))
                                            
            name = ''.join([name, ' (%d)' % (max(current_indices) + 1)])
        self.notebook.SetPageText(idx, name)
    
            
    def onSavePlot(self, *args):
        self.get_active_plot().save_figure_as_image()
        
        
        
        
        
