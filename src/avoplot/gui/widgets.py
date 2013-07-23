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
The widgets module contains a set of convenience widgets for building
control panels for elements.
"""

import wx

class SettingBase(wx.BoxSizer):
    """
    Base class for settings controls.
    """
    def __init__(self, parent, label):
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)
        if label:
            text = wx.StaticText(parent, -1, label)
            self.Add(text, 0, wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_LEFT)
            

class ColourSetting(SettingBase):
    """
    A text label next to a wx colour picker control.
    """
    def __init__(self, parent, label, default_colour, callback):
        SettingBase.__init__(self, parent, label)
        
        cp = wx.ColourPickerCtrl(parent, -1, default_colour)
        self.Add(cp, 0 , wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_LEFT)
        wx.EVT_COLOURPICKER_CHANGED(parent,cp.GetId(), callback)


class TextSetting(SettingBase):
    """
    A text label next to a wx text entry control.
    """
    def __init__(self, parent, label, default_text, callback):
        SettingBase.__init__(self, parent, label)
        
        self.tc = wx.TextCtrl(parent, -1, value=default_text, 
                              style=wx.TE_PROCESS_ENTER)
        wx.EVT_TEXT(parent, self.tc.GetId(), callback)
        self.Add(self.tc, 1, wx.ALIGN_CENTRE_VERTICAL)


class ChoiceSetting(SettingBase):
    """
    A text label next to a wx choice control.
    """   
    def __init__(self, parent, label, current_selection, selections, callback):
        SettingBase.__init__(self, parent, label)
        
        lb = wx.Choice(parent, -1, choices=selections)
        self.Add(lb, 0, wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_LEFT)
        lb.SetStringSelection(current_selection)
        
        wx.EVT_CHOICE(parent, lb.GetId(), callback)
        
        
        
        