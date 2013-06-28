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
from matplotlib.backends.backend_wx import _load_bitmap as load_matplotlib_bitmap

class MainToolbar(wx.ToolBar):
    def __init__(self,parent):
        self.parent = parent

        
        wx.ToolBar.__init__(self,parent, wx.ID_ANY)
        
        #file tools    
        new_tool = self.AddTool(-1, wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR), shortHelpString="New plot")    
        self.save_tool = self.AddTool(-1, wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR), shortHelpString="Save plot")
        self.AddSeparator()

        #plot navigation tools
        self.home_tool = self.AddTool(-1, wx.ArtProvider.GetBitmap(wx.ART_GO_HOME, wx.ART_TOOLBAR),shortHelpString="Return to initial zoom setting")
        self.zoom_tool = self.AddCheckTool(-1, load_matplotlib_bitmap('zoom_to_rect.png'), shortHelp="Zoom selection")
        self.move_tool = self.AddCheckTool(-1, load_matplotlib_bitmap('move.png'),shortHelp='Pan',longHelp='Pan with left, zoom with right')
        #self.follow_data_tool = self.AddCheckTool(-1, wx.ArtProvider.GetBitmap("avoplot_grid",wx.ART_TOOLBAR),shortHelp='Inspect the data values' )
        self.AddSeparator()

        #self.grid_tool = self.AddCheckTool(-1, wx.ArtProvider.GetBitmap("avoplot_grid",wx.ART_TOOLBAR),shortHelp='Toggle gridlines' )
        #self.AddSeparator()
        
        self.Realize()
        self.enable_plot_tools(False)
        
        #register events
        wx.EVT_TOOL(self.parent, new_tool.GetId(), self.onNew)
        wx.EVT_TOOL(self.parent, self.save_tool.GetId(), self.parent.onSavePlot)        
        wx.EVT_TOOL(self.parent, self.home_tool.GetId(), self.onHome)
        wx.EVT_TOOL(self.parent, self.zoom_tool.GetId(), self.onZoom)
        wx.EVT_TOOL(self.parent, self.move_tool.GetId(), self.onMove)
        #wx.EVT_TOOL(self.parent, self.follow_data_tool.GetId(), self.on_follow_data)
        #wx.EVT_TOOL(self.parent, self.grid_tool.GetId(), self.onGrid)
   
    
    def enable_plot_tools(self, state):
        self.EnableTool(self.save_tool.GetId(),state)
        self.EnableTool(self.home_tool.GetId(),state)
        self.EnableTool(self.move_tool.GetId(),state)
        self.EnableTool(self.zoom_tool.GetId(),state)
        #self.EnableTool(self.grid_tool.GetId(),state)
   
    
    def onNew(self,evnt):
        """Handle menu button pressed."""
        x, y = self.GetPositionTuple()
        w, h = self.GetSizeTuple()
        self.PopupMenuXY(self.parent.menu.new_menu, x, y+h-34)

        
    def onHome(self, evnt):
        p = self.parent.get_active_plot()
        
        if p is not None:
            p.go_home()
 
    
    def onZoom(self,evnt):
        self.ToggleTool(self.move_tool.GetId(),False) 
        for p in self.parent.get_all_pages():
            p.zoom()

   
    def onMove(self,evnt):
        self.ToggleTool(self.zoom_tool.GetId(),False) 
        for p in self.parent.get_all_pages():
            p.pan()

    
#    def onGrid(self, evnt):     
#        gridstate = self.GetToolState(self.grid_tool.GetId())
#        p = self.parent.get_active_plot()
#        if p is not None:
#            p.gridlines(gridstate)
       
            
    def on_follow_data(self, evnt):
        #TODO - disable the other navigation tools on all the plots
        follow_state = self.GetToolState(self.follow_data_tool.GetId())
        for p in self.parent.get_all_pages():
            p.follow_data(follow_state)
            
        