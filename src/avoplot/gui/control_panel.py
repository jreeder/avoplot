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
from avoplot import core

class ControlPanel(aui.AuiNotebook):
    def __init__(self,parent):
        super(ControlPanel, self).__init__(parent, id=wx.ID_ANY, 
                                           style=wx.NB_TOP|wx.CLIP_CHILDREN)
        self._current_element = None
        core.EVT_AVOPLOT_ELEM_SELECT(self, self.on_element_select)
        core.EVT_AVOPLOT_ELEM_DELETE(self, self.on_element_delete)
       
    def set_control_panels(self, control_panels):
        """
        Sets the control panels shown in the notebook. 'control_panels' should
        be a list of AvoPlotControlPanelBase objects.
        """
        self.Freeze()
        self.Show(False)
        if self._current_element is not None:
            while self.GetPageCount():
                p = self.GetPage(0)
                self.RemovePage(0)
                p.Show(False)
                p.Reparent(p.old_parent)
        
        for p in control_panels:
            p.Reparent(self)
            self.AddPage(p, p.get_name())

        self.Show(True)
        self.Thaw()
        
        #send a size event to force redraw of window contents - this is only
        #really needed in windows
        self.SendSizeEvent()
    
    
    def on_element_delete(self, evnt):

        el = evnt.element

        if el == self._current_element:
            while self.GetPageCount():
                self.DeletePage(0)
            self._current_element = None
    
    
    def on_element_select(self, evnt):
        el = evnt.element
        if el != self._current_element: 
            self.set_control_panels(el.get_control_panels())
            self._current_element = el
