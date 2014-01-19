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
import wx.lib.newevent
import avoplot
import avoplot.plugins
from avoplot import core
from avoplot import figure

#define some new events to be used when panes are hidden/restored
AvoPlotCtrlPanelChangeState, EVT_AVOPLOT_CTRL_PANEL_STATE = wx.lib.newevent.NewEvent()
AvoPlotNavPanelChangeState, EVT_AVOPLOT_NAV_PANEL_STATE = wx.lib.newevent.NewEvent()

#TODO - add keyboard shortcuts

class CallbackWrapper:
    """
    Thin wrapper class to allow callables along with a set of arguments for them 
    to be set as callback handlers.
    """
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        
    def __call__(self, *args):
        self.func(*self.args, **self.kwargs)
        
        

def get_subplot_right_click_menu(subplot):
    """
    Returns a wx.Menu object which is relevant for the subplot which was passed
    as an arg. This ensures that only menu entries provided by plugins which
    are compatible with the subplot are included. For example, there is no point
    in the menu for a 2D subplot to have a "New 3D data series" option.
    """
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
    """
    The main program menu.
    """
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
        """
        Event handler for AvoPlotElementSelect events. Just keeps track of which
        element is currently selected.
        """
        el = evnt.element

        if isinstance(el, figure.AvoPlotFigure):
            self.__current_figure = el 
    
    
    def on_element_add(self, evnt):
        """
        Event handler for AvoPlotElementAdd events. Enables menu entries when 
        there are a sufficient number of figures open for it to make sense to do
        so. For example - you can't split the display if you only have one
        figure open.
        """
        
        el = evnt.element
        
        if isinstance(el, figure.AvoPlotFigure):
            self.__current_figure = el
            #self.save_data_entry.Enable(enable=True)
            self.save_plot_entry.Enable(enable=True)
            self.__figure_count += 1
        
        if self.__figure_count > 1:
            self.h_split.Enable(enable=True)
            self.v_split.Enable(enable=True)
            self.unsplit.Enable(enable=True)
    
    
    def on_element_delete(self, evnt):
        """
        Event handler for AvoPlotElementDelete events. Disables menu entries when 
        there are an insufficient number of figures open for them to make sense.
        For example - you can't save a figure if there are none open.
        """
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
        """
        Creates the file menu for the main menubar.
        """
        file_menu = wx.Menu()
        
        self.new_menu = create_the_New_menu(self.parent)    
        file_menu.AppendSubMenu(self.new_menu, "New")
        
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
        """
        Event handler for File->Save menu events. Opens a dialog to allow the 
        user to save the currently selected figure as an image.
        """
        if self.__current_figure is not None:
            self.__current_figure.save_figure_as_image()
        
        
    def create_help_menu(self):
        """
        Creates the help menu for the main menubar
        """
        help_menu = wx.Menu()
        
        about = help_menu.Append(-1, "&About", "Information about the %s"
                                 " program."%avoplot.PROG_SHORT_NAME)
        
        #register the event handlers
        wx.EVT_MENU(self.parent,about.GetId(), self.onAbout)
        
        self.Append(help_menu, "&Help")
    
    
    def create_view_menu(self):
        """
        Creates the view menu for the main menubar
        """        
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
        """
        Event handler for View->Control Panel menu events. Sends a 
        AvoPlotCtrlPanelChangeState event to the main window and lets that sort 
        out hiding/restoring the pane.
        """
        evt = AvoPlotCtrlPanelChangeState(state=evnt.Checked())
        wx.PostEvent(self.parent, evt)
    
    
    def on_ctrl_panel_change_state(self, evnt):
        """
        Event handler for AvoPlotCtrlPanelChangeState events. Updates the 
        toggle state of the View->Control Panel menu entry.
        """
        self.ctrl_panel.Check(evnt.state)
        
    
    def on_show_nav_panel(self, evnt):
        """
        Event handler for View->Navigation Panel menu events. Sends a 
        AvoPlotNavPanelChangeState event to the main window and lets that sort 
        out hiding/restoring the pane.
        """
        evt = AvoPlotNavPanelChangeState(state=evnt.Checked())
        wx.PostEvent(self.parent, evt)
    
    
    def on_nav_panel_change_state(self, evnt):
        """
        Event handler for AvoPlotNavPanelChangeState events. Updates the 
        toggle state of the View->Navigation Panel menu entry.
        """
        self.nav_panel.Check(evnt.state)
        
        
    def onAbout(self, evnt):
        """
        Event handler for Help->About menu events. Creates a standard "About" 
        dialog.
        """   
        about_info = wx.AboutDialogInfo()
        about_info.SetIcon(wx.ArtProvider.GetIcon('avoplot',
                                                  size=wx.Size(96,96)))
        about_info.SetName(avoplot.PROG_LONG_NAME)
        about_info.SetVersion(str(avoplot.VERSION))
        about_info.SetCopyright(avoplot.COPYRIGHT)
        about_info.SetDescription(avoplot.LONG_DESCRIPTION)
        
        #read the license text from the COPYING file that was installed along
        #with the program
        #with open(avoplot.get_license_file(),'r') as ifp:
        #    license_ = ifp.read()
        about_info.SetLicense(avoplot.COPY_PERMISSION)
        
        about_info.AddArtist("Yves Moussallam <ym286@cam.ac.uk>")
        about_info.AddDeveloper("Nial Peters <nonbiostudent@hotmail.com>")
        
        wx.AboutBox(about_info)
        
        
def create_the_New_menu(parent):
    """
    Creates and returns a new wxMenu object which contains the "File->New" 
    entries. These are read from the plugins that are currently registered.
    
    The relevant event handlers for the menu entries are also registered by this
    function.
    """
    #create submenu for creating new plots of different types.
    menu = wx.Menu()      
    sub_menus = {}
    
    #get the menu entries from the plugins
    for p in avoplot.plugins.get_plugins().values():
        labels = p.get_menu_entry_labels()
        if not labels:
            continue #this plugin does not have menu entries
        
        cur_submenu = menu
        cur_submenu_dict = sub_menus
        
        for i in range(len(labels)-1):
            
            if not cur_submenu_dict.has_key(labels[i]):
                cur_submenu_dict[labels[i]] = ({},wx.Menu())
                cur_submenu.AppendSubMenu(cur_submenu_dict[labels[i]][1], 
                                          labels[i]) 
                
            cur_submenu = cur_submenu_dict[labels[i]][1]
            cur_submenu_dict = cur_submenu_dict[labels[i]][0]
        
        #register the plugin's create_new method as the event handler for
        #this entry
        entry = cur_submenu.Append(-1, labels[-1], 
                                       p.get_menu_entry_tooltip())
        wx.EVT_MENU(parent,entry.GetId(), p.create_new)
    
 
    return menu

        
        
class TabRightClickMenu(wx.Menu):
    """
    The menu displayed when a tab in the plots panel (which is an AuiNotebook) 
    is right clicked on.
    """
    def __init__(self, plots_frame):
        
        wx.Menu.__init__(self)
        
        self.plots_frame = plots_frame
                       
        rename = self.Append(wx.ID_ANY,"Rename", "Rename the current tab")
        wx.EVT_MENU(self, rename.GetId(), self.plots_frame.rename_current_figure)
        self.AppendSeparator()
        
        h_split = self.Append(-1, "Split Horizontal", "Split the current plot "
                              "into a new pane")
        v_split = self.Append(-1, "Split Vertical", "Split the current plot "
                              "into a new pane")
        wx.EVT_MENU(self, h_split.GetId(), self.plots_frame.split_figure_horiz)
        wx.EVT_MENU(self, v_split.GetId(), self.plots_frame.split_figure_vert)
        
        self.AppendSeparator()
        close_current = self.Append(wx.ID_ANY,"Close", "Close the current tab")
        wx.EVT_MENU(self, close_current.GetId(), self.close_current)
        
        close_others = self.Append(wx.ID_ANY,"Close Others", "Close other tabs")
        wx.EVT_MENU(self, close_others.GetId(), self.close_others)
        
        close_all = self.Append(wx.ID_ANY,"Close All", "Close all tabs")
        wx.EVT_MENU(self, close_all.GetId(), self.close_all)
    
    
    def close_current(self, evnt):
        """
        Event handler for "Close" menu events. Closes the currently selected
        figure.
        """
        idx = self.plots_frame.GetSelection()
        fig = self.plots_frame.GetPage(idx)
        fig.delete()
    
    
    def close_others(self, evnt):
        """
        Event handler for "Close Others" menu events. Closes all figures except 
        the currently selected one.
        """        
        cur_idx = self.plots_frame.GetSelection()
        self.plots_frame.Freeze()
        figs_to_delete = []
        #close all the plots with lower index than current
        for i in range(cur_idx):
            figs_to_delete.append(self.plots_frame.GetPage(i))

        #close all plots with higher index
        for i in range(cur_idx +1, self.plots_frame.GetPageCount()):
            figs_to_delete.append(self.plots_frame.GetPage(i))
            
        for f in figs_to_delete:
            f.delete()
        
        self.plots_frame.Thaw()
    
    
    def close_all(self, evnt):
        """
        Event handler for "Close All" menu events. Closes all figures.
        """         
        
        self.plots_frame.Freeze()

        figs_to_delete = [self.plots_frame.GetPage(i) for i in range(self.plots_frame.GetPageCount())]
        
        for fig in figs_to_delete:
            fig.delete()

        self.plots_frame.Thaw()
        
        
        