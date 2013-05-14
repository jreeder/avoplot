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
#from wx.lib.agw.flatnotebook import FlatNotebook, EVT_FLATNOTEBOOK_PAGE_CHANGED, EVT_FLATNOTEBOOK_PAGE_CLOSED, FNB_FANCY_TABS, FNB_X_ON_TAB,FNB_NO_X_BUTTON, EVT_FLATNOTEBOOK_PAGE_CLOSING
from wx.aui import AuiNotebook, EVT_AUINOTEBOOK_PAGE_CHANGED, EVT_AUINOTEBOOK_PAGE_CLOSE, EVT_AUINOTEBOOK_PAGE_CLOSED,AUI_NB_DEFAULT_STYLE
from wx.aui import EVT_AUINOTEBOOK_TAB_RIGHT_DOWN
from avoplot.gui.artwork import AvoplotArtProvider
from avoplot.gui import menu
from avoplot.gui import toolbar
from avoplot import persist



class MainFrame(wx.Frame):      
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "AvoPlot")
        
        #set up the icon for the frame
        art = AvoplotArtProvider()
        wx.ArtProvider.Push(art)
        self.SetIcon(art.GetIcon("AvoPlot"))
        
        #create the persistant settings object
        self.persistant = persist.PersistantStorage()
        
        #create the menu
        self.menu = menu.MainMenu(self)
        self.SetMenuBar(menu.MainMenu(self))
        
        #create the toolbar
        self.toolbar = toolbar.MainToolbar(self)
        self.SetToolBar(self.toolbar)
        
        #create the notebook
        self.notebook = AuiNotebook(self, id = wx.ID_ANY, style=AUI_NB_DEFAULT_STYLE)
        
        wx.EVT_CLOSE(self, self.onClose)
        EVT_AUINOTEBOOK_PAGE_CLOSE(self, self.notebook.GetId(), self.onTabClose)
        EVT_AUINOTEBOOK_PAGE_CLOSED(self, self.notebook.GetId(), self.onTabChange)
        EVT_AUINOTEBOOK_PAGE_CHANGED(self, self.notebook.GetId(), self.onTabChange)
        EVT_AUINOTEBOOK_TAB_RIGHT_DOWN(self, self.notebook.GetId(), self.onTabRightClick)
        self.Show()
    
    
    def onTabClose(self, evnt):
        p = self.get_active_plot()
        p.close()
   
        
    def onTabRightClick(self, evnt):
        self.notebook.SetSelection(evnt.GetSelection())
        context_menu = wx.Menu()
        rename = context_menu.Append(wx.ID_ANY,"Rename", "Rename the current tab")
        wx.EVT_MENU(self, rename.GetId(), self.rename_current_tab)
        self.PopupMenu(context_menu)
    
    
    def rename_current_tab(self, evnt):
        page_idx = self.notebook.GetSelection()
        d = wx.TextEntryDialog(self, "Plot name:","Rename", defaultValue=self.notebook.GetPageText(page_idx))
        if d.ShowModal() == wx.ID_OK:
            new_name = d.GetValue()
            if new_name and not new_name.isspace():
                self.notebook.SetPageText(page_idx,d.GetValue())
            
            
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
        #close each plot in turn in order to shut down the plotting threads
        for i in range(0,self.notebook.GetPageCount(),):
            self.notebook.GetPage(i).close()
        self.Destroy()
   
   
    def add_plot_tab(self, plot, name, select=True):
        self.notebook.AddPage(plot, name, select=select)

            
            
    def onSavePlot(self, *args):
        self.get_active_plot().save_plot()
        
        
        
        
        
