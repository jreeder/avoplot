import wx
import sys


class GridPropertiesEditor(wx.Dialog):

    def __init__(self, parent, subplot):
        
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Gridline properties")
        
        #set up the icon for the frame
        if sys.platform == "win32":
            self.SetIcon(wx.ArtProvider.GetIcon("avoplot", size=(16, 16)))
        else:
            self.SetIcon(wx.ArtProvider.GetIcon("avoplot", size=(64, 64)))
        
        self.CentreOnParent()
        self.ShowModal()
        
        
        
        