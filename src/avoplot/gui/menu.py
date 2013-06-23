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
import os.path
import avoplot
import avoplot.plugins

#TODO - add keyboard shortcuts

def get_subplot_right_click_menu(subplot):
    menu = wx.Menu()
    new_series_menu = wx.Menu()
    menu.AppendSubMenu(new_series_menu,"Add series")
    sub_menus = {}
    for p in avoplot.plugins.get_plugins().values():
        if not isinstance(subplot, p.get_supported_series_type().get_supported_subplot_type()):
            continue
        labels = p.get_menu_entry_labels()
        if not labels:
            continue #this plugin does not have menu entries
        
        cur_submenu = new_series_menu
        cur_submenu_dict = sub_menus
        
        for i in range(len(labels)-1):
            
            if not cur_submenu_dict.has_key(labels[i]):
                cur_submenu_dict[labels[i]] = ({},wx.Menu())
                cur_submenu.AppendSubMenu(cur_submenu_dict[labels[i]][1], 
                                          labels[i]) 
                
            cur_submenu = cur_submenu_dict[labels[i]][1]
            cur_submenu_dict = cur_submenu_dict[labels[i]][0]
            
            #now add the menu entry
            entry = cur_submenu.Append(-1, labels[-1], 
                                           p.get_menu_entry_tooltip())
            
            f = lambda x: p.plot_into_subplot(subplot)
            wx.EVT_MENU(subplot.get_figure().parent,entry.GetId(), f)
    return menu
        

class MainMenu(wx.MenuBar):
    def __init__(self, parent):
        wx.MenuBar.__init__(self)
        self.parent=parent
        self.create_file_menu()
        self.create_view_menu()
        self.create_help_menu()
        
                
    def create_file_menu(self):
        file_menu = wx.Menu()
        
        #create submenu for creating new plots of different types.
        new_submenu = wx.Menu()      
        sub_menus = {}
        
        #get the entries from the plugins
        for p in avoplot.plugins.get_plugins().values():
            labels = p.get_menu_entry_labels()
            if not labels:
                continue #this plugin does not have menu entries
            
            cur_submenu = new_submenu
            cur_submenu_dict = sub_menus
            
            for i in range(len(labels)-1):
                
                if not cur_submenu_dict.has_key(labels[i]):
                    cur_submenu_dict[labels[i]] = ({},wx.Menu())
                    cur_submenu.AppendSubMenu(cur_submenu_dict[labels[i]][1], 
                                              labels[i]) 
                    
                cur_submenu = cur_submenu_dict[labels[i]][1]
                cur_submenu_dict = cur_submenu_dict[labels[i]][0]
            
            #now add the menu entry
            entry = cur_submenu.Append(-1, labels[-1], 
                                           p.get_menu_entry_tooltip())
            wx.EVT_MENU(self.parent,entry.GetId(), p.create_new)
        
     
        self.new_menu = new_submenu      
        file_menu.AppendSubMenu(new_submenu, "New")
        
        #save controls
        save_data = file_menu.Append(-1, "&Export Data", "Save the current "
                                     "plot data.")
        save_plot = file_menu.Append(wx.ID_SAVE, "&Save Plot", "Save the "
                                     "current plot.")

        exit = file_menu.Append(wx.ID_EXIT, "&Exit", "Exit AvoPlot.")
        
        #register the event handlers
        wx.EVT_MENU(self.parent,exit.GetId(), self.parent.onClose)
        wx.EVT_MENU(self.parent,save_plot.GetId(), self.parent.onSavePlot)
                
        #add the menu item to the MenuBar (self)
        self.Append(file_menu, "&File")
    
    
    def create_help_menu(self):
        help_menu = wx.Menu()
        
        about = help_menu.Append(-1, "&About", "Information about the %s"
                                 " program."%avoplot.PROG_SHORT_NAME)
        
        #register the event handlers
        wx.EVT_MENU(self.parent,about.GetId(), self.onAbout)
        
        self.Append(help_menu, "&Help")
    
    
    def create_view_menu(self):
        view_menu = wx.Menu()
        h_split = view_menu.Append(-1, "Split &Horizontal", "Split the current"
                                   " plot into a new pane")
        v_split = view_menu.Append(-1, "Split &Vertical", "Split the current"
                                   " plot into a new pane")
        unsplit = view_menu.Append(-1, "&Unsplit", "Collapse all tabs into a "
                                   "single pane")
        
        wx.EVT_MENU(self.parent, h_split.GetId(), self.parent.split_plot_horiz)
        wx.EVT_MENU(self.parent, v_split.GetId(), self.parent.split_plot_vert)
        wx.EVT_MENU(self.parent, unsplit.GetId(), self.parent.unsplit_panes)
        self.Append(view_menu, '&View')
    
    
    def onAbout(self, evnt):       
        about_info = wx.AboutDialogInfo()
        about_info.SetIcon(wx.ArtProvider.GetIcon('avoplot',
                                                  size=wx.Size(96,96)))
        about_info.SetName(avoplot.PROG_LONG_NAME)
        about_info.SetVersion(str(avoplot.VERSION))
        about_info.SetCopyright(avoplot.COPYRIGHT)
        about_info.SetDescription(avoplot.LONG_DESCRIPTION)
        with open(os.path.join(avoplot.get_avoplot_sys_dir(),'COPYING'),
                  'r') as ifp:
            license = ifp.read()
        about_info.SetLicense(license)
        
        about_info.AddArtist("Yves Moussallam <ym286@cam.ac.uk>")
        about_info.AddDeveloper("Nial Peters <nonbiostudent@hotmail.com>")
        
        wx.AboutBox(about_info)
        
        
        
        
class TabRightClickMenu(wx.Menu):
    def __init__(self, main_frame):
        
        wx.Menu.__init__(self)
        
        self.main_frame = main_frame
                       
        rename = self.Append(wx.ID_ANY,"Rename", "Rename the current tab")
        wx.EVT_MENU(self, rename.GetId(), self.main_frame.rename_current_tab)
        self.AppendSeparator()
        
        h_split = self.Append(-1, "Split Horizontal", "Split the current plot "
                              "into a new pane")
        v_split = self.Append(-1, "Split Vertical", "Split the current plot "
                              "into a new pane")
        wx.EVT_MENU(self, h_split.GetId(), self.main_frame.split_plot_horiz)
        wx.EVT_MENU(self, v_split.GetId(), self.main_frame.split_plot_vert)
        
        self.AppendSeparator()
        close_current = self.Append(wx.ID_ANY,"Close", "Close the current tab")
        wx.EVT_MENU(self, close_current.GetId(), self.close_current)
        
        close_others = self.Append(wx.ID_ANY,"Close Others", "Close other tabs")
        wx.EVT_MENU(self, close_others.GetId(), self.close_others)
        
        close_all = self.Append(wx.ID_ANY,"Close All", "Close all tabs")
        wx.EVT_MENU(self, close_all.GetId(), self.close_all)
    
    
    def close_current(self, evnt):
        idx = self.main_frame.notebook.GetSelection()
        self.main_frame.close_plot(idx)
    
    
    def close_others(self, evnt):
        cur_idx = self.main_frame.notebook.GetSelection()
        self.main_frame.Freeze()
        #close all the plots with lower index than current
        for i in range(cur_idx):
            self.main_frame.close_plot(0)
        
        #close all plots with higher index
        for i in range(self.main_frame.notebook.GetPageCount() - 1):
            self.main_frame.close_plot(1)
        
        self.main_frame.Thaw()
    
    
    def close_all(self, evnt):
        self.main_frame.Freeze()
        idx = self.main_frame.notebook.GetSelection()
       
        while idx >= 0:
            self.main_frame.close_plot(idx)
            idx = self.main_frame.notebook.GetSelection()
        self.main_frame.Thaw()
        
        
        