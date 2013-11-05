# -*- coding: utf-8 -*- 
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
import warnings
from wx.lib.agw import floatspin 
import threading
import numpy
import collections
import matplotlib.colors
import os
import time
from datetime import datetime


#new data type to represent line styles and their relevant properties
LineType = collections.namedtuple('LineType',['name','mpl_symbol','has_width'])  

#create a list of all the line types and their properties - the order of
#this list determines the order that they appear in the drop down menu
available_lines = [
                   LineType('None','None', False),
                   LineType('____','-', True),
                   LineType('------','--',True),
                   LineType('.-.-.-','-.', True),
                   LineType('.......',':',True)
                   ]

#build some mappings between line properties and their indices in the list
#of available lines
line_symbol_to_idx_map = {}
line_name_to_idx_map = {}
for i,m in enumerate(available_lines):
    line_symbol_to_idx_map[m.mpl_symbol] = i
    line_name_to_idx_map[m.name] = i


#new data type to represent markers and their relevant properties
MarkerType = collections.namedtuple('MarkerType',['name','mpl_symbol','has_size', 
                                                  'has_fill', 'has_edge'])        

#create a list of all the marker types and their properties - the order of
#this list determines the order that they appear in the drop down menu
available_markers = [
                     MarkerType('None','None', False, False, False),
                     MarkerType(u'●', '.',True, True, True),
                     MarkerType('+','+', True, False, True),
                     MarkerType(u'◯','o', True, True, True),
                     MarkerType('X','x', True, False, True),
                     MarkerType(u'△','^', True, True, True),
                     MarkerType(u'▽','v', True, True, True),
                     MarkerType(u'◁','<', True, True, True),
                     MarkerType(u'▷','>', True, True, True),
                     MarkerType(u'◻','s', True, True, True),
                     MarkerType(u'◇','D', True, True, True),
                     MarkerType(u'⋄','d', True, True, True),
                     MarkerType(u'⬠','p', True, True, True),
                     MarkerType(u'⬡','h', True, True, True),
                     MarkerType(u'☆','*', True, True, True),
                     MarkerType('_','_', True, False, True),
                     MarkerType('|','|', True, False, True),
                     MarkerType('.',',', False, True, False)
                     ]

#build some mappings between marker properties and their indices in the list
#of available markers
marker_symbol_to_idx_map = {}
marker_name_to_idx_map = {}
for i,m in enumerate(available_markers):
    marker_symbol_to_idx_map[m.mpl_symbol] = i
    marker_name_to_idx_map[m.name] = i




class LineStyleEditorPanel(wx.Panel):
    
    def __init__(self, parent, mpl_lines, update_command):
        
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.mpl_lines = mpl_lines
        self.update_command = update_command
        
        line_ctrls_szr = wx.FlexGridSizer(3, 2, vgap=5, hgap=2)
               
        #line style
        line_ctrls_szr.Add(wx.StaticText(self, wx.ID_ANY, "Style:"), 0,
                           wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT)
        self.linestyle_choice = wx.Choice(self, wx.ID_ANY, choices=[l.name for l in available_lines])
        line_ctrls_szr.Add(self.linestyle_choice, 0,
                           wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT)
        wx.EVT_CHOICE(self, self.linestyle_choice.GetId(), self.on_linestyle)
        
        #line thickness
        self.line_weight_ctrl_txt = wx.StaticText(self, wx.ID_ANY, "Thickness:")
        self.line_weight_ctrl = floatspin.FloatSpin(self, wx.ID_ANY, min_val=0.1, max_val=50.0,
                                     value=mpl_lines[0].get_linewidth(), increment=0.1, digits=2)
        line_ctrls_szr.Add(self.line_weight_ctrl_txt, 0,
                           wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT)
        line_ctrls_szr.Add(self.line_weight_ctrl, 0,
                           wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT)
        floatspin.EVT_FLOATSPIN(self, self.line_weight_ctrl.GetId(), self.on_linewidth)
        
        #line colour
        line_col = matplotlib.colors.colorConverter.to_rgb(mpl_lines[0].get_color())
        line_col = (255 * line_col[0], 255 * line_col[1], 255 * line_col[2])
        self.line_colour_picker_txt = wx.StaticText(self, wx.ID_ANY, "Colour:")
        self.line_colour_picker = wx.ColourPickerCtrl(self, -1, line_col)
        line_ctrls_szr.Add(self.line_colour_picker_txt, 0,
                           wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT)
        line_ctrls_szr.Add(self.line_colour_picker, 0 ,
                          wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT)
        wx.EVT_COLOURPICKER_CHANGED(self, self.line_colour_picker.GetId(), self.on_line_colour_change)
    
        #set the line selection to that of the data
        #it is possible that the line will have been set to something that
        #avoplot does not yet support - if so, default to None and issue warning
        if line_symbol_to_idx_map.has_key(mpl_lines[0].get_linestyle()):
            #everything is fine
            current_line_idx = line_symbol_to_idx_map[mpl_lines[0].get_linestyle()]
        else:
            current_line_idx = 0
            warnings.warn("Data series has an unsupported line style. "
                          "Defaulting to a line style of \'None\' instead.")
        
        #update the GUI appropriately for the current line selection
        self.linestyle_choice.SetSelection(current_line_idx)
        self.update_line_controls(available_lines[current_line_idx])
        
        self.SetSizer(line_ctrls_szr)
        line_ctrls_szr.Fit(self)
        self.SetAutoLayout(True)
        
    def on_line_colour_change(self, evnt):
        """
        Event handler for line colour change events.
        """
        for l in self.mpl_lines:
            l.set_color(evnt.GetColour().GetAsString(wx.C2S_HTML_SYNTAX))
        self.update_command()
        
    
    def on_linestyle(self, evnt):
        """
        Event handler for line style change events.
        """
        line_idx = line_name_to_idx_map[evnt.GetString()]
        new_line = available_lines[line_idx]
        self.update_line_controls(new_line)
        for l in self.mpl_lines:
            l.set_linestyle(new_line.mpl_symbol)
        
        self.update_command()
        
        
    
    def on_linewidth(self, evnt):
        """
        Event handler for line thickness change events.
        """
        for l in self.mpl_lines:
            l.set_linewidth(self.line_weight_ctrl.GetValue())
        
        self.update_command()
                
    
    def update_line_controls(self, current_line):
        """
        If val==True then disables the line properties controls,
        else enables them.
        """
        #show/hide the colour and width controls
        self.line_colour_picker.Show(current_line.has_width)
        self.line_colour_picker_txt.Show(current_line.has_width)
        self.line_weight_ctrl.Show(current_line.has_width)
        self.line_weight_ctrl_txt.Show(current_line.has_width)
        
        self.SendSizeEvent()