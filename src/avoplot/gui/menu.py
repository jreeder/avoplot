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
import avoplot.plugins

#TODO - add keyboard shortcuts

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
        menu_items = {}
        
        for p in avoplot.plugins.get_plugins().values():
            menu_data = p.get_onNew_handler()
            
            if not menu_data[1] or menu_data[1].isspace():
                if menu_items.has_key(menu_data[0]):
                    raise RuntimeError("Two or more plugins have tried to register different callbacks for the same menu entry.")
                menu_items[menu_data[0]] = menu_data
            else:
                if sub_menus.has_key(menu_data[0]):
                    sub_menus[menu_data[0]].append(menu_data)
                else:
                    sub_menus[menu_data[0]] = [menu_data]
        
        #put menu items above submenus
        for item_name in sorted(menu_items.keys()):
            name, junk, desc, handler = menu_items[item_name]
            temp_item = new_submenu.Append(-1, item_name, desc)
            wx.EVT_MENU(self.parent,temp_item.GetId(), handler)
        
        for menu_name in sorted(sub_menus.keys()):
            temp_submenu = wx.Menu()            
            for junk, name, desc, handler in sub_menus[menu_name]:
                    
                temp_menu_item = temp_submenu.Append(-1, name, desc)
                wx.EVT_MENU(self.parent,temp_menu_item.GetId(), handler)
            
            new_submenu.AppendSubMenu(temp_submenu, menu_name)
     
        self.new_menu = new_submenu      
        file_menu.AppendSubMenu(new_submenu, "New")
        
        #save controls
        save_data = file_menu.Append(-1, "&Export Data", "Save the current plot data.")
        save_plot = file_menu.Append(wx.ID_SAVE, "&Save Plot", "Save the current plot.")

        exit = file_menu.Append(wx.ID_EXIT, "&Exit", "Exit AvoPlot.")
        
        #register the event handlers
        wx.EVT_MENU(self.parent,exit.GetId(), self.parent.onClose)
        wx.EVT_MENU(self.parent,save_plot.GetId(), self.parent.onSavePlot)
                
        #add the menu item to the MenuBar (self)
        self.Append(file_menu, "&File")
    
    
    def create_help_menu(self):
        help_menu = wx.Menu()
        
        about = help_menu.Append(-1, "&About", "Information about the AvoPlot program.")
        
        #register the event handlers
        wx.EVT_MENU(self.parent,about.GetId(), self.onAbout)
        
        self.Append(help_menu, "&Help")
    
    
    def create_view_menu(self):
        view_menu = wx.Menu()
        h_split = view_menu.Append(-1, "Split &Horizontal", "Split the current plot into a new pane")
        v_split = view_menu.Append(-1, "Split &Vertical", "Split the current plot into a new pane")
        unsplit = view_menu.Append(-1, "&Unsplit", "Collapse all tabs into a single pane")
        wx.EVT_MENU(self.parent, h_split.GetId(), self.parent.split_plot_horiz)
        wx.EVT_MENU(self.parent, v_split.GetId(), self.parent.split_plot_vert)
        wx.EVT_MENU(self.parent, unsplit.GetId(), self.parent.unsplit_panes)
        self.Append(view_menu, '&View')
    
    
    def onAbout(self, evnt):
        about_info = wx.AboutDialogInfo()
        
        about_info.SetName("AvoPlot")
        about_info.SetVersion(str(avoplot.__version__))
        about_info.SetCopyright("(C) 2013 Nial Peters <nonbiostudent@hotmail.com>")
        about_info.SetDescription("A plotting tool for visualising DOAS data.")
        
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
        
        h_split = self.Append(-1, "Split Horizontal", "Split the current plot into a new pane")
        v_split = self.Append(-1, "Split Vertical", "Split the current plot into a new pane")
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
        
        
        