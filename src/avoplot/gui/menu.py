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
import os.path
import avoplot
import avoplot.plugins
from avoplot import core
from avoplot import figure

AvoPlotCtrlPanelChangeState, EVT_AVOPLOT_CTRL_PANEL_STATE = wx.lib.newevent.NewEvent()
AvoPlotNavPanelChangeState, EVT_AVOPLOT_NAV_PANEL_STATE = wx.lib.newevent.NewEvent()

#TODO - add keyboard shortcuts

class CallbackWrapper:
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        
    def __call__(self, *args):
        self.func(*self.args, **self.kwargs)
        
        

def get_subplot_right_click_menu(subplot):
    menu = wx.Menu()
    new_series_menu = wx.Menu()
    menu.AppendSubMenu(new_series_menu,"Add series")
    sub_menus = {}
    
    for p in avoplot.plugins.get_plugins().values():
        if not issubclass(p.get_supported_series_type().get_supported_subplot_type(), subplot.__class__):
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
        entry = cur_submenu.Append(-1, labels[-1], p.get_menu_entry_tooltip())
        callback = CallbackWrapper(p.plot_into_subplot, subplot)
        wx.EVT_MENU(subplot.get_figure().parent,entry.GetId(), callback)
    
    return menu
        

class MainMenu(wx.MenuBar):
    def __init__(self, parent):
        wx.MenuBar.__init__(self)
        self.parent=parent
        self.__current_figure = None
        self.__figure_count = 0
        self.create_file_menu()
        self.create_view_menu()
        self.create_help_menu()
        
        core.EVT_AVOPLOT_ELEM_ADD(self, self.on_element_add)
        core.EVT_AVOPLOT_ELEM_DELETE(self, self.on_element_delete)
        core.EVT_AVOPLOT_ELEM_SELECT(self, self.on_element_select)
    
    
    
    def on_element_select(self, evnt):
        el = evnt.element

        if isinstance(el, figure.AvoPlotFigure):
            self.__current_figure = el 
    
    
    def on_element_add(self, evnt):
        el = evnt.element
        
        if isinstance(el, figure.AvoPlotFigure):
            self.__current_figure = el
            self.save_data_entry.Enable(enable=True)
            self.save_plot_entry.Enable(enable=True)
            self.__figure_count += 1
        
        if self.__figure_count > 1:
            self.h_split.Enable(enable=True)
            self.v_split.Enable(enable=True)
            self.unsplit.Enable(enable=True)
    
    
    def on_element_delete(self, evnt):
        el = evnt.element
        if isinstance(el, figure.AvoPlotFigure):
            if el == self.__current_figure:
                self.__current_figure = None
            
            self.__figure_count -= 1
            
            if not self.__figure_count:
                self.save_data_entry.Enable(enable=False)
                self.save_plot_entry.Enable(enable=False)
            
            if self.__figure_count < 2:
                self.h_split.Enable(enable=False)
                self.v_split.Enable(enable=False)
                self.unsplit.Enable(enable=False)
        
                        
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
        self.save_data_entry = file_menu.Append(-1, "&Export Data", "Save the current "
                                     "plot data.")
        self.save_plot_entry = file_menu.Append(wx.ID_SAVE, "&Save Plot", "Save the "
                                     "current plot.")
        
        self.save_data_entry.Enable(enable=False)
        self.save_plot_entry.Enable(enable=False)
        
        exit = file_menu.Append(wx.ID_EXIT, "&Exit", "Exit AvoPlot.")
        
        #register the event handlers
        wx.EVT_MENU(self.parent,exit.GetId(), self.parent.on_close)
        wx.EVT_MENU(self.parent,self.save_plot_entry.GetId(), self.on_save_plot)
                
        #add the menu item to the MenuBar (self)
        self.Append(file_menu, "&File")
        
    
    def on_save_plot(self, evnt):
        if self.__current_figure is not None:
            self.__current_figure.save_figure_as_image()
        
        
    def create_help_menu(self):
        help_menu = wx.Menu()
        
        about = help_menu.Append(-1, "&About", "Information about the %s"
                                 " program."%avoplot.PROG_SHORT_NAME)
        
        #register the event handlers
        wx.EVT_MENU(self.parent,about.GetId(), self.onAbout)
        
        self.Append(help_menu, "&Help")
    
    
    def create_view_menu(self):
        view_menu = wx.Menu()
        self.h_split = view_menu.Append(-1, "Split &Horizontal", "Split the current"
                                   " plot into a new pane")
        self.v_split = view_menu.Append(-1, "Split &Vertical", "Split the current"
                                   " plot into a new pane")
        self.unsplit = view_menu.Append(-1, "&Unsplit", "Collapse all tabs into a "
                                   "single pane")
        self.h_split.Enable(enable=False)
        self.v_split.Enable(enable=False)
        self.unsplit.Enable(enable=False)
        
        view_menu.AppendSeparator()
        
        self.ctrl_panel = view_menu.AppendCheckItem(-1,"Control Panel", 
                                               'Show or hide the plot controls')
        view_menu.Check(self.ctrl_panel.GetId(), True)
        
        self.nav_panel = view_menu.AppendCheckItem(-1,"Navigation Panel", 
                                              'Show or hide the plot '
                                              'navigation panel')
        view_menu.Check(self.nav_panel.GetId(), True)
        
        wx.EVT_MENU(self.parent, self.h_split.GetId(), self.parent.plots_panel.split_figure_horiz)
        wx.EVT_MENU(self.parent, self.v_split.GetId(), self.parent.plots_panel.split_figure_vert)
        wx.EVT_MENU(self.parent, self.unsplit.GetId(), self.parent.plots_panel.unsplit_panes)
        wx.EVT_MENU(self.parent, self.ctrl_panel.GetId(), self.on_show_ctrl_panel)
        wx.EVT_MENU(self.parent, self.nav_panel.GetId(), self.on_show_nav_panel)
        
        EVT_AVOPLOT_CTRL_PANEL_STATE(self, self.on_ctrl_panel_change_state)
        EVT_AVOPLOT_NAV_PANEL_STATE(self, self.on_nav_panel_change_state)
        
        self.Append(view_menu, '&View')
    
    
    def on_show_ctrl_panel(self, evnt):
        evt = AvoPlotCtrlPanelChangeState(state=evnt.Checked())
        wx.PostEvent(self.parent, evt)
    
    
    def on_ctrl_panel_change_state(self, evnt):
        self.ctrl_panel.Check(evnt.state)
        
    
    def on_show_nav_panel(self, evnt):
        evt = AvoPlotNavPanelChangeState(state=evnt.Checked())
        wx.PostEvent(self.parent, evt)
    
    
    def on_nav_panel_change_state(self, evnt):
        self.nav_panel.Check(evnt.state)
        
        
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
        wx.EVT_MENU(self, rename.GetId(), self.main_frame.rename_current_figure)
        self.AppendSeparator()
        
        h_split = self.Append(-1, "Split Horizontal", "Split the current plot "
                              "into a new pane")
        v_split = self.Append(-1, "Split Vertical", "Split the current plot "
                              "into a new pane")
        wx.EVT_MENU(self, h_split.GetId(), self.main_frame.split_figure_horiz)
        wx.EVT_MENU(self, v_split.GetId(), self.main_frame.split_figure_vert)
        
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
        
        
        