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

class ControlPanel(wx.Notebook):
    def __init__(self,parent):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY)
    
       
    def set_control_panels(self, control_panels):
        """
        Sets the control panels shown in the notebook. 'control_panels' should
        be a list of AvoPlotControlPanelBase objects.
        """
        while self.GetPageCount():
            self.RemovePage(0)
        
        for p in control_panels:
            self.Add(p, p.name) 
    
    
    def on_element_selection(self, evnt):
        el = evnt.element
        
        self.set_control_panels(el.get_control_panels())
        
        print "handled element change event"