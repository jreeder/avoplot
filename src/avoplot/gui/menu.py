import wx
import avoplot

#TODO - add keyboard shortcuts

class MainMenu(wx.MenuBar):
    def __init__(self, parent):
        wx.MenuBar.__init__(self)
        self.parent=parent
        self.create_file_menu()
        
        self.create_help_menu()
        
                
    def create_file_menu(self):
        file_menu = wx.Menu()
        
        #create submenu for creating new plots of different types.
        new_submenu = wx.Menu()      
        new_spectrum_plot = new_submenu.Append(-1, "&Spectrum plot", "Plot a spectrum file.")
        new_time_plot = new_submenu.Append(-1, "&Time plot", "Create a new time series plot.")
        new_realtime_time_plot = new_submenu.Append(-1, "&Realtime time plot", "Create a new realtime time series plot.")
        new_scatter_plot = new_submenu.Append(-1, "S&catter plot", "Create a new scatter plot.")
        new_realtime_scatter_plot = new_submenu.Append(-1, "R&ealtime scatter plot", "Create a new realtime scatter plot.")
        self.new_menu = new_submenu      
        file_menu.AppendSubMenu(new_submenu, "New")
        
        #save controls
        save_data = file_menu.Append(-1, "&Export Data", "Save the current plot data.")
        save_plot = file_menu.Append(wx.ID_SAVE, "&Save Plot", "Save the current plot.")

        
        exit = file_menu.Append(wx.ID_EXIT, "&Exit", "Exit AvoPlot.")
        
        #register the event handlers
        wx.EVT_MENU(self.parent,exit.GetId(), self.parent.onClose)
        wx.EVT_MENU(self.parent,new_spectrum_plot.GetId(), self.parent.onSpectrumPlot)
        wx.EVT_MENU(self.parent,new_time_plot.GetId(), self.parent.onTimePlot)
        wx.EVT_MENU(self.parent,new_realtime_time_plot.GetId(), self.parent.onRealtimeTimePlot)
        wx.EVT_MENU(self.parent,save_plot.GetId(), self.parent.onSavePlot)
                
        #add the menu item to the MenuBar (self)
        self.Append(file_menu, "&File")
    
    
    def create_help_menu(self):
        help_menu = wx.Menu()
        
        about = help_menu.Append(-1, "&About", "Information about the AvoPlot program.")
        
        #register the event handlers
        wx.EVT_MENU(self.parent,about.GetId(), self.onAbout)
        
        self.Append(help_menu, "&Help")
    
    
    def onAbout(self, evnt):
        about_info = wx.AboutDialogInfo()
        
        about_info.SetName("AvoPlot")
        about_info.SetVersion(str(avoplot.__version__))
        about_info.SetCopyright("(C) 2013 Nial Peters <nonbiostudent@hotmail.com>")
        about_info.SetDescription("A plotting tool for visualising DOAS data.")
        
        about_info.AddArtist("Yves Moussallam <ym286@cam.ac.uk>")
        about_info.AddDeveloper("Nial Peters <nonbiostudent@hotmail.com>")
        
        wx.AboutBox(about_info)