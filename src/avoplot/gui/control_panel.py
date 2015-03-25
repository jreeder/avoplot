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
        
        #remove the close buttons from the tabs - there is no way to restore
        #controlpanel tabs that get closed.
        style = aui.AUI_NB_DEFAULT_STYLE & ~(aui.AUI_NB_CLOSE_BUTTON |
                                             aui.AUI_NB_CLOSE_ON_ACTIVE_TAB |
                                             aui.AUI_NB_CLOSE_ON_ALL_TABS)
        
        super(ControlPanel, self).__init__(parent, id=wx.ID_ANY, 
                                           agwStyle=style)
        
        self._current_element = None
        self.__layouts = {} #stores the layout of the control panels (keys are IDs)
        self.__selections = {} #stores the last page selected (keys are IDS)
        
        core.EVT_AVOPLOT_ELEM_SELECT(self, self.on_element_select)
        core.EVT_AVOPLOT_ELEM_DELETE(self, self.on_element_delete)
        core.EVT_AVOPLOT_ELEM_ADD(self, self.on_element_add)
    
        aui.EVT_AUINOTEBOOK_PAGE_CHANGING(self, self.GetId(), self.on_page_changing)
        aui.EVT_AUINOTEBOOK_PAGE_CHANGED(self, self.GetId(), self.on_page_changed)
        
        
    def on_page_changing(self, evnt):
        """
        Event handler for page changing events. Calls the on_control_panel_inactive()
        method on the control panel that is being de-selected.
        """
        page_idx = self.GetSelection()
        page  = self.GetPage(page_idx)
        page.on_control_panel_inactive()
        evnt.Skip()
    
    
    def on_page_changed(self, evnt):
        """
        Event handler for page changed events. Calls the on_control_panel_active()
        method on the control panel that has been newly selected.
        """
        page_idx = self.GetSelection()
        page  = self.GetPage(page_idx)
        page.on_control_panel_active()
        evnt.Skip()
    
    
    def reset_control_panels(self):
        """
        Resets the control panels shown in the notebook to those for the 
        currently selected element.
        """
        if self._current_element is not None:
            self.set_control_panels(self._current_element, force=True)
    
       
    def set_control_panels(self, element, force=False):
        """
        Sets the control panels shown in the notebook. 'control_panels' should
        be a list of AvoPlotControlPanelBase objects.
        """
        currently_visible = self.IsShown()

        control_panels = element.get_control_panels()
        
        self.Freeze()
        self.Show(False)

        if self._current_element is not None:
            
            #store the control panel layout for this element
            layout = self.SavePerspective()
            self.__layouts[self._current_element.get_avoplot_id()] = layout
            
            #store which page is currently selected, so that we can restore
            #the selection when this element is selected in the future (note
            #that the current selection is not part of the layout information)
            sel = self.GetSelection()
            self.__selections[self._current_element.get_avoplot_id()] = sel

            while self.GetPageCount():
                # get rid of the old pages 
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

        #only load the saved perspective if there are actually some control panels
        #to arrange. Otherwise when the session element gets selected 
        #(e.g. when the final figure gets closed) then this will try to load an
        #invalid perspective
        if control_panels and self.__layouts.has_key(element.get_avoplot_id()):
            self.LoadPerspective(self.__layouts[element.get_avoplot_id()])
        
        #Restore the user's previous page selection.
        if (len(control_panels) > 1 and 
            self.__selections.has_key(element.get_avoplot_id())):
            
            self.SetSelection(self.__selections[element.get_avoplot_id()])
        
        self.Thaw()
        
        #send a size event to force redraw of window contents - this is only
        #really needed in windows
        self.SendSizeEvent()
        
        #perform any operations needed prior to display
        for p in reversed(control_panels):
            p.on_display() 
        
        if currently_visible or force:    
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
        
