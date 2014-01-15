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
from wx.lib.agw import aui

from avoplot import core
"""
The control panel holds all the controls for the currently selected element.
It is created as a dockable frame managed by the AuiManager of the main AvoPlot
window.
"""

class ControlPanel(aui.AuiNotebook):
    """
    Notebook control which holds all the controls for the currently selected
    element. Each set of controls (as returned by element.get_control_panels())
    is added as a new tab in the notebook.
    """
    def __init__(self,parent):
        super(ControlPanel, self).__init__(parent, id=wx.ID_ANY, 
                                           style=wx.NB_TOP|wx.CLIP_CHILDREN)
        self._current_element = None
        self.__layouts = {}
        
        core.EVT_AVOPLOT_ELEM_SELECT(self, self.on_element_select)
        core.EVT_AVOPLOT_ELEM_DELETE(self, self.on_element_delete)
        core.EVT_AVOPLOT_ELEM_ADD(self, self.on_element_add)
    
        aui.EVT_AUINOTEBOOK_PAGE_CHANGING(self, self.GetId(), self.on_page_changing)
        aui.EVT_AUINOTEBOOK_PAGE_CHANGED(self, self.GetId(), self.on_page_changed)
        
        
    def on_page_changing(self, evnt):
        page_idx = self.GetSelection()
        page  = self.GetPage(page_idx)
        page.on_control_panel_inactive()
        evnt.Skip()
    
    def on_page_changed(self, evnt):
        page_idx = self.GetSelection()
        page  = self.GetPage(page_idx)
        page.on_control_panel_active()
        evnt.Skip()
    
       
    def set_control_panels(self, element):
        """
        Sets the control panels shown in the notebook. 'control_panels' should
        be a list of AvoPlotControlPanelBase objects.
        """
        control_panels = element.get_control_panels()
        
        self.Freeze()
        self.Show(False)
        if self._current_element is not None:
            
            #store the control panel layout for this element
            layout = self.SavePerspective()
            self.__layouts[self._current_element.get_avoplot_id()] = layout
            while self.GetPageCount():
                # get rid of the old pages and reparent them back to whatever
                #window was their parent before they were added to the notebook
                p = self.GetPage(0)
                
                #need to call this explicitly, since we remove the page rather
                #then changing it
                p.on_control_panel_inactive()
                
                self.RemovePage(0)
                p.Show(False)
        
        #reverse the order so that plugin-defined panels appear first
        for p in reversed(control_panels):
            #AuiNotebook requires that any pages have the notebook as a parent -
            #so reparent all the panels to make it so!
            if not p.is_initialised():
                p.setup(self)
            
            self.AddPage(p, p.get_name())
            

        if self.__layouts.has_key(element.get_avoplot_id()):
            self.LoadPerspective(self.__layouts[element.get_avoplot_id()])
        self.Thaw()
        
        #send a size event to force redraw of window contents - this is only
        #really needed in windows
        self.SendSizeEvent()
        
        #perform any operations needed prior to display
        for p in reversed(control_panels):
            p.on_display() 
            
        self.Show(True)
    
    
    def on_element_delete(self, evnt):
        """
        Event handler for element delete events. Removes any control panels 
        associated with the deleted element from the notebook.
        
        If the element is not the currently selected element, then the event
        gets passed through to all pages currently in the control panel
        """
        el = evnt.element

        if el == self._current_element:
            while self.GetPageCount():
                # get rid of the old pages and reparent them back to whatever
                #window was their parent before they were added to the notebook
                p = self.GetPage(0)
                self.RemovePage(0)
                p.Show(False)
            
            self._current_element = None
        else:
            for i in range(self.GetPageCount()):
                p = self.GetPage(i)
                wx.PostEvent(p, evnt)
        
        #remove any stored layouts relating to this element.
        try:
            self.__layouts.pop(el.get_avoplot_id())
        except KeyError:
            pass
    
    
    def on_element_add(self, evnt):
        """
        Event handler for element add events. Passes the event through to
        all pages currently in the control panel
        """
        for i in range(self.GetPageCount()):
            p = self.GetPage(i)
            wx.PostEvent(p, evnt)
    
    
    def on_element_select(self, evnt):
        """
        Event handler for element select events. Adds any relevant control 
        panels for the newly selected element to the notebook.
        """

        el = evnt.element

        if el != self._current_element: 
            self.set_control_panels(el)
            self._current_element = el
        
        #pass the event through to all the pages in the control panel
        for i in range(self.GetPageCount()):
            p = self.GetPage(i)
            wx.PostEvent(p, evnt)
        
