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
import re
import wx
import  wx.lib.newevent

AvoPlotElementSelectEvent, EVT_AVOPLOT_ELEM_SELECT = wx.lib.newevent.NewEvent()
AvoPlotElementRenameEvent, EVT_AVOPLOT_ELEM_RENAME = wx.lib.newevent.NewEvent()
AvoPlotElementDeleteEvent, EVT_AVOPLOT_ELEM_DELETE = wx.lib.newevent.NewEvent()
AvoPlotElementAddEvent, EVT_AVOPLOT_ELEM_ADD = wx.lib.newevent.NewEvent()

def new_id():
    """
    Returns a unique ID number
    """
    if not hasattr(new_id,'n'):
        new_id.n = 0
    new_id.n += 1
    return new_id.n

  
class AvoPlotElementBase(object):
    def __init__(self, name):
        self.__avoplot_id = new_id()
        self.__control_panels = []
        self.__parent_element = None
        self.__child_elements = set()
        
        self.set_name(name)
    
    
    def _add_child_element(self, el):
        assert isinstance(el, AvoPlotElementBase)
        assert el != self
        assert el != self.__parent_element
        self.__child_elements.add(el)
        
        #send the element delete event
        evt = AvoPlotElementAddEvent(element=el)
        wx.PostEvent(wx.GetApp().GetTopWindow(), evt)
    
    
    def _remove_child_element(self, el):
        self.__child_elements.remove(el)

    
    
    def delete(self):
        
        while self.__child_elements:
            el = list(self.__child_elements)[-1]
            el.delete()
            
        self.set_parent_element(None)
        
        #send the element delete event
        evt = AvoPlotElementDeleteEvent(element=self)
        wx.PostEvent(wx.GetApp().GetTopWindow(), evt)

    
    
    def get_control_panels(self):
        for cp in self.__control_panels:
            assert cp.is_initialised()
        
        return self.__control_panels
       
    
    def get_child_elements(self):
        return self.__child_elements
    
    
    def setup_controls(self, parent):
        for cp in self.__control_panels:
            assert not cp.is_initialised()
            cp.setup(parent)
    
    
    def get_name(self):
        return self.__name
    
    
    def get_parent_element(self):
        return self.__parent_element
    
       
    def add_control_panel(self, panel):
        assert isinstance(panel, controls.AvoPlotControlPanelBase)
        self.__control_panels.append(panel)
    
    
    def get_avoplot_id(self):
        return self.__avoplot_id
    
    
    def set_name(self, name):
        #assert type(name) == str, "name must be a string" 

        name = str(name)
               
        #if the parent of this element already has a child with this name
        #then append a number to the end of it
        if self.__parent_element is not None:
            sibling_names = []
            for c in self.__parent_element.get_child_elements():
                if c == self:
                    continue
                sibling_names.append(c.get_name())
            
            if sibling_names.count(name) > 0:
                current_indices = [1]
                #this name is already in use - find what the 
                #highest index of current use is (don't want to go back to
                #lower numbers if some intermediate tab is closed)

                for n in sibling_names:
                    if not n.startswith(name):
                        continue
                    n = n[len(name):].strip()
                    
                    if n:
                        match = re.match(r'\(([0-9]+)\)', n)
                        if match:
                            current_indices.append(int(match.groups()[0]))
                                                
                name = ''.join([name, ' (%d)' % (max(current_indices) + 1)])
        self.__name = name
        
        #send an element rename event
        evt = AvoPlotElementRenameEvent(element=self)
        wx.PostEvent(wx.GetApp().GetTopWindow(), evt)
    
    
    def set_parent_element(self, parent):
        assert isinstance(parent, AvoPlotElementBase) or parent is None
        if self.__parent_element is not None:
            self.__parent_element._remove_child_element(self)
        
        self.__parent_element = parent
        
        if parent is not None:
            self.__parent_element._add_child_element(self)
        
            #update the name (the new parent might have more children with 
            #the same name
            self.set_name(self.get_name())
    
    
    def set_selected(self):
        #fire an element selected event
        evt = AvoPlotElementSelectEvent(element=self)
        wx.PostEvent(wx.GetApp().GetTopWindow(), evt)
    
    
    
        
        