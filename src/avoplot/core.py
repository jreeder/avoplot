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
"""
The core module provides the base class for AvoPlot elements, which are used to
represent the hierarchy of plots - i.e. a figure may contain many subplots, a
subplot may contain many data series etc.

The element framework is designed to cope with the fact that many different 
components of the GUI may modify plot elements and all of these components
will need to be notified of the changes. For example, a figure may be renamed 
by using the right-click menu on the its tab in the plots panel. It can also
be renamed using the navigation panel - both of these panels need to be notified
when the name of a figure gets changed. The way this is implemented is as 
follows: the panel doing the renaming calls figure.rename_element(). This 
changes the name of the element and generates an AvoPlotElementRenameEvent. Both 
the plots panel and the navigation panel handle this event and use it to update 
their appearance. Adding and deleting elements works in a similar way.

"""
import avoplot
from avoplot import controls
import re
import wx
import  wx.lib.newevent

#create new events for avoplot element objects
AvoPlotElementSelectEvent, EVT_AVOPLOT_ELEM_SELECT = wx.lib.newevent.NewEvent()
AvoPlotElementRenameEvent, EVT_AVOPLOT_ELEM_RENAME = wx.lib.newevent.NewEvent()
AvoPlotElementDeleteEvent, EVT_AVOPLOT_ELEM_DELETE = wx.lib.newevent.NewEvent()
AvoPlotElementAddEvent, EVT_AVOPLOT_ELEM_ADD = wx.lib.newevent.NewEvent()


def new_id():
    """
    Returns a unique ID number. This is used to identify different elements 
    across a single instance of the AvoPlot program.
    """
    #TODO - this is going to break when save/load gets implemented
    if not hasattr(new_id, 'n'):
        new_id.n = 0
    new_id.n += 1
    return new_id.n
    
    
  
  
class AvoPlotElementBase(object):
    """
    Base class for all AvoPlot elements. Elements are essentially a container
    class that holds child elements. For example, a figure element can contain 
    several subplots as its children.
    """
    def __init__(self, name):
        self.__avoplot_id = new_id()
        self.__control_panels = []
        self.__parent_element = None
        self.__child_elements = set()
        self.__alive = True
        self.set_name(name)
    
    
    def _add_child_element(self, el):
        """
        Don't call this directly - instead call set_parent_element() on the 
        child.
        """
        #sanity checks
        assert isinstance(el, AvoPlotElementBase)
        assert el != self
        assert el != self.__parent_element
        
        self.__child_elements.add(el)
        
        #send the element delete event
        evt = AvoPlotElementAddEvent(element=el)
        wx.PostEvent(wx.GetApp().GetTopWindow(), evt)
    
    
    def _remove_child_element(self, el):
        """
        Don't call this directly - instead call set_parent_element(None) on the
        child.
        """
        self.__child_elements.remove(el)
    
    
    def delete(self):
        """
        Sets the element's parent to None, and calls the delete() method of any
        child elements. Generates a AvoPlotElementDeleteEvent event.
        """
        if not self.__alive:
            print "warning! delete() called on element %s more than once"%self.get_name()
            return
        self.__alive = False
        #recursively call delete on all child elements
        while self.__child_elements:
            el = list(self.__child_elements)[-1]
            el.delete()
            
        #destroy self - setting parent to None should bring the ref-count
        #to zero in terms of the element tree at least.
        self.set_parent_element(None)
        
        #send the element delete event
        evt = AvoPlotElementDeleteEvent(element=self)
        wx.PostEvent(wx.GetApp().GetTopWindow(), evt)
        
        avoplot.call_on_idle(self._destroy)
    
       
    def _destroy(self):
        """
        The destroy method is used to perform "final" deletion operations
        such as calling Destroy on wx window objects etc. This is called 
        once the event loop is empty (triggered on an EVT_IDLE) to prevent
        dead object access exceptions. Subclasses that need to override this
        method should make sure that they call the base class's method too.
        """
        for p in self.get_control_panels():
            p.Destroy()
        self.__control_panels = []
        
    
    def get_control_panels(self):
        """
        Returns a list of control panel objects (instances of 
        avoplot.controls.AvoPlotControlPanelBase) that relate to the element.
        """
        for cp in self.__control_panels:
            assert cp.is_initialised()
        
        return self.__control_panels
       
    
    def get_child_elements(self):
        """
        Returns a list of child elements (instances of AvoPlotElementBase or its
        subclasses).
        """
        return self.__child_elements
    
    
    def setup_controls(self, parent):
        """
        Calls the setup method of all the control panels associated with this
        element. parent should be the parent window for the controls.
        """
        for cp in self.__control_panels:
            assert not cp.is_initialised()
            cp.setup(parent)
    
    
    def get_name(self):
        """
        Returns the elements name.
        """
        return self.__name
    
    
    def get_parent_element(self):
        """
        Returns the parent element of this element (this will be an instance of 
        AvoPlotElementBase or one of its subclasses)
        """
        return self.__parent_element
    
       
    def add_control_panel(self, panel):
        """
        Adds a control to the element. This must be an instance of a subclass of
        avoplot.controls.AvoPlotControlPanelBase.
        """
        assert isinstance(panel, controls.AvoPlotControlPanelBase)
        self.__control_panels.append(panel)
    
    
    def get_avoplot_id(self):
        """
        Returns the element's unique id number (integer)
        """
        return self.__avoplot_id
    
    
    def set_name(self, name):
        """
        Sets the name of the element. If the parent element already contains
        a child element with the specified name, then \'(n)\' will be appended
        to the name assigned (where n is an integer counter). This will generate
        an AvoPlotElementRenameEvent.
        """ 
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
                                                
                name = ''.join([name, ' (%d)'%(max(current_indices) + 1)])
        self.__name = name
        
        #send an element rename event
        evt = AvoPlotElementRenameEvent(element=self)
        wx.PostEvent(wx.GetApp().GetTopWindow(), evt)
    
    
    def set_parent_element(self, parent):
        """
        Reparents the element to the element specified. parent must be an 
        instance of AvoPlotElementBase or one of its subclasses, or None.
        
        If the new parent already has a child of the same name, then the 
        element's name will be updated using set_name().
        """
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
        """
        Generates an AvoPlotElementSelectEvent for the element.
        """
        if self.__alive:
            #fire an element selected event
            evt = AvoPlotElementSelectEvent(element=self)
            wx.PostEvent(wx.GetApp().GetTopWindow(), evt)
        else:
            print "Warning! Attempt to select deleted object\'%s\'"%self.get_name()
    
    
    def update(self):
        """
        Redraws the element in the display. This should be called after the 
        element is changed to reflect the changes in the display. This must
        be overridden in subclasses.
        """
        raise (NotImplementedError, "Subclasses of AvoPlotElementBase must "
               "override the update method")
    
    