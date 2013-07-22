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

from avoplot import core
from avoplot import figure

class MainToolbar(wx.ToolBar):
    def __init__(self,parent):
        self.parent = parent
        
        self.__active_figure = None
        self.__all_figures = set()
        
        wx.ToolBar.__init__(self,parent, wx.ID_ANY)
        
        #file tools    
        self.new_tool = self.AddTool(-1, wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR), shortHelpString="New plot")    
        self.save_tool = self.AddTool(-1, wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR), shortHelpString="Save plot")
        self.AddSeparator()

        #plot navigation tools
        self.home_tool = self.AddTool(-1, wx.ArtProvider.GetBitmap(wx.ART_GO_HOME, wx.ART_TOOLBAR),shortHelpString="Return to initial zoom setting")
        self.zoom_tool = self.AddCheckTool(-1, load_matplotlib_bitmap('zoom_to_rect.png'), shortHelp="Zoom selection")
        self.pan_tool = self.AddCheckTool(-1, load_matplotlib_bitmap('move.png'),shortHelp='Pan',longHelp='Pan with left, zoom with right')
        #self.follow_data_tool = self.AddCheckTool(-1, wx.ArtProvider.GetBitmap("avoplot_grid",wx.ART_TOOLBAR),shortHelp='Inspect the data values' )
        self.AddSeparator()

        #self.grid_tool = self.AddCheckTool(-1, wx.ArtProvider.GetBitmap("avoplot_grid",wx.ART_TOOLBAR),shortHelp='Toggle gridlines' )
        #self.AddSeparator()
        
        self.Realize()
        self.enable_plot_tools(False)
        
        #register avoplot event handlers
        core.EVT_AVOPLOT_ELEM_ADD(self, self.on_element_add)
        core.EVT_AVOPLOT_ELEM_SELECT(self, self.on_element_select)
        core.EVT_AVOPLOT_ELEM_DELETE(self, self.on_element_delete)
        
        #register events
        wx.EVT_TOOL(self.parent, self.new_tool.GetId(), self.on_new)
        wx.EVT_TOOL(self.parent, self.save_tool.GetId(), self.on_save_plot)        
        wx.EVT_TOOL(self.parent, self.home_tool.GetId(), self.on_home)
        wx.EVT_TOOL(self.parent, self.zoom_tool.GetId(), self.on_zoom)
        wx.EVT_TOOL(self.parent, self.pan_tool.GetId(), self.on_pan)
        #wx.EVT_TOOL(self.parent, self.follow_data_tool.GetId(), self.on_follow_data)
        #wx.EVT_TOOL(self.parent, self.grid_tool.GetId(), self.onGrid)
   
    
    def on_element_add(self, evnt):
        el = evnt.element
        if isinstance(el, figure.AvoPlotFigure):
            if not self.__all_figures:
                self.enable_plot_tools(True)
            
            #enable the zoom/pan tools for this figure (if they are currently
            #selected in the toolbar)
            if self.GetToolState(self.pan_tool.GetId()):
                el.pan()
            elif self.GetToolState(self.zoom_tool.GetId()):
                el.zoom()
            
            self.__all_figures.add(el)
    
    
    def on_element_delete(self, evnt):
        el = evnt.element
        if isinstance(el, figure.AvoPlotFigure):
            self.__all_figures.remove(el)
            if not self.__all_figures:
                self.enable_plot_tools(False)
    
    
    def on_element_select(self, evnt):
        el = evnt.element
        if isinstance(el, figure.AvoPlotFigure):
            self.__active_figure = el
        
    
    
    def enable_plot_tools(self, state):
        self.EnableTool(self.save_tool.GetId(),state)
        self.EnableTool(self.home_tool.GetId(),state)
        self.EnableTool(self.pan_tool.GetId(),state)
        self.EnableTool(self.zoom_tool.GetId(),state)
        #self.EnableTool(self.grid_tool.GetId(),state)
   
    
    def on_new(self,evnt):
        """Handle menu button pressed."""
        #Get the position of the toolbar relative to
        #the frame. This will be the upper left corner of the first tool
        bar_pos = self.GetScreenPosition()-self.parent.GetScreenPosition()

        # This is the position of the tool along the tool bar (1st, 2nd, 3rd, etc...)
        tool_index = self.GetToolPos(evnt.GetId())

        # Get the size of the tool
        tool_size = self.GetToolSize()

        # This is the lowerr left corner of the clicked tool
        lower_left_pos = (bar_pos[0]+self.GetToolSeparation()*(tool_index+1)+tool_size[0]*tool_index, bar_pos[1]+tool_size[1]+self.GetToolSeparation())#-tool_size[1])

        menu_pos = (lower_left_pos[0]-bar_pos[0],lower_left_pos[1]-bar_pos[1])
        self.PopupMenu(self.parent.menu.new_menu, menu_pos)

        
    def on_home(self, evnt):
        if self.__active_figure is not None:
            self.__active_figure.go_home()
 
    
    def on_zoom(self,evnt):
        self.ToggleTool(self.pan_tool.GetId(),False) 
        for p in self.__all_figures:
            p.zoom()

   
    def on_pan(self,evnt):
        self.ToggleTool(self.zoom_tool.GetId(),False) 
        for p in self.__all_figures:
            p.pan()

    
    def on_save_plot(self, *args):

        if self.__active_figure is not None:
            self.__active_figure.save_figure_as_image()
       
            
    def on_follow_data(self, evnt):
        #TODO - disable the other navigation tools on all the plots
        follow_state = self.GetToolState(self.follow_data_tool.GetId())
        for p in self.__all_figures:
            p.follow_data(follow_state)
            
        