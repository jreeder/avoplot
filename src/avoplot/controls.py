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

class AvoPlotControlPanelBase(wx.ScrolledWindow):
    """
    Base class for control panels - these are the tabs shown in the 
    "Control Panel" frame.
    """
    
    def __init__(self, name):
        self.__name = name
        self.__sizer = wx.BoxSizer(wx.VERTICAL)
        self.__is_initialised = False
        
           
    def setup(self, parent):
        """
        Control panels are typically instanciated before their parent frame is
        known. Therefore, the majority of the setup of the panel should be done
        in the setup method - this is passed the parent window as its only 
        argument. Subclasses that override this method should be sure to call
        the setup method of their parent class *before* doing anything else.
        """
        #call the __init__ method of the wx.Window class (we can do this now
        #we know who our parent is)
        super(AvoPlotControlPanelBase, self).__init__(parent, wx.ID_ANY)
        
        
        self.SetScrollRate(2, 2)
        self.SetSizer(self.__sizer)
        self.__sizer.Fit(self)
        self.SetAutoLayout(True)
        self.__is_initialised = True
    
    
    def on_control_panel_active(self):
        """
        This method will be called automatically each time the control panel 
        becomes the active control panel (i.e. the user selects it, it has
        focus). This can be overridden by subclasses to perform needed actions
        on control panel activation (e.g. enabling tools etc.)
        """
        pass
    
    
    def on_control_panel_inactive(self):
        """
        This method will be called automatically each time the control panel
        stops being the active control panel (i.e. the user selects a different
        one). This can be overridden by subclasses to perform needed actions
        on control panel de-activation (e.g. disabling tools etc.)
        """
        pass
    
    
    def on_display(self):
        """
        This method will be called each time the control panel is displayed i.e.
        every time that the element that the control panel operates on is 
        selected. It can be overridden by subclasses in order to perform 
        processing before it is displayed (for example updating lists of 
        available data series etc.)
        """
        pass
    
    
    def is_initialised(self):
        """
        Returns True if the setup() method has already been run for this 
        control panel, False otherwise.
        """
        return self.__is_initialised
    
    
    def get_name(self):
        """
        Returns the name of this control panel - this will be the text displayed
        in the tab heading.
        """
        return self.__name
    
    
    def Add(self,*args, **kwargs):
        """
        Adds a new element into the control panel's sizer - *args and **kwargs
        are the same as for a wx.BoxSizer.
        """
        self.__sizer.Add(*args, **kwargs)
        