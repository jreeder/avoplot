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
from avoplot import controls
import wx
import  wx.lib.newevent


AvoPlotElementChangeEvent, EVT_AVOPLOT_ELEM_CHANGE = wx.lib.newevent.NewEvent()


def new_id():
    """
    Returns a unique ID number
    """
    if not hasattr(new_id,'n'):
        new_id.n = 0
    new_id.n += 1
    return new_id.n



    
    
class AvoPlotElementBase(object):
    def __init__(self):
        self.__avoplot_id = new_id()
        self.__control_panels = []
    
    
    def get_control_panels(self):
        return self._control_panels
       
       
    def add_control_panel(self, panel):
        assert isinstance(panel, controls.AvoPlotControlPanelBase)
        self._control_panels.append(panel)
    
    
    def get_avoplot_id(self):
        return self.__avoplot_id
    
    
    def set_selected(self):
        #fire an element selected event
        evt = AvoPlotElementChangeEvent(element=self)
        wx.PostEvent(wx.GetApp().GetTopWindow(), evt)
    
    
    
        
        