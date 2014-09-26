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
import collections
import matplotlib.colors

from avoplot.gui import widgets


#new data type to represent line styles and their relevant properties
LineType = collections.namedtuple('LineType',['name','mpl_symbol','has_width'])  

#create a list of all the line types and their properties - the order of
#this list determines the order that they appear in the drop down menu
all_available_lines = [
                       LineType('','None', False), #None has to come first
                       LineType('____','-', True),
                       LineType('------','--',True),
                       LineType('.-.-.-','-.', True),
                       LineType('.......',':',True)
                       ]


#new data type to represent markers and their relevant properties
MarkerType = collections.namedtuple('MarkerType',['bitmap','mpl_symbol','has_size', 
                                                  'has_fill', 'has_edge'])        

#create a list of all the marker types and their properties - the order of
#this list determines the order that they appear in the drop down menu
#TODO - include NullBitmap here properly
all_available_markers = [
                     MarkerType('avoplot_nullbitmap','None', False, False, False),
                     MarkerType('avoplot_marker_point', '.',True, True, True),
                     MarkerType('avoplot_marker_plus','+', True, False, True),
                     MarkerType('avoplot_marker_circle','o', True, True, True),
                     MarkerType('avoplot_marker_cross','x', True, False, True),
                     MarkerType('avoplot_marker_uptriangle','^', True, True, True),
                     MarkerType('avoplot_marker_downtriangle','v', True, True, True),
                     MarkerType('avoplot_marker_lefttriangle','<', True, True, True),
                     MarkerType('avoplot_marker_righttriangle','>', True, True, True),
                     MarkerType('avoplot_marker_square','s', True, True, True),
                     MarkerType('avoplot_marker_diamond','D', True, True, True),
                     MarkerType('avoplot_marker_thindiamond','d', True, True, True),
                     MarkerType('avoplot_marker_pentagon','p', True, True, True),
                     MarkerType('avoplot_marker_hexagon','h', True, True, True),
                     MarkerType('avoplot_marker_star','*', True, True, True),
                     MarkerType('avoplot_marker_hline','_', True, False, True),
                     MarkerType('avoplot_marker_vline','|', True, False, True)
                     ]


class LineStyleEditorPanel(wx.Panel):
    
    def __init__(self, parent, mpl_lines, update_command, 
                 linestyles=all_available_lines):
        """
        Panel with controls to allow the user to change the style of a series
        line.
        """    
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.mpl_lines = mpl_lines
        self.parent = parent
        self.update_command = update_command
        self.__available_lines = linestyles
        
        self.__line_symbol_to_idx_map = {}
        self.__line_name_to_idx_map = {}
        for i,m in enumerate(self.__available_lines):
            self.__line_symbol_to_idx_map[m.mpl_symbol] = i
            self.__line_name_to_idx_map[m.name] = i
        
        line_ctrls_szr = wx.FlexGridSizer(cols=2, vgap=5, hgap=2)
        
               
        #line style
        line_ctrls_szr.Add(wx.StaticText(self, wx.ID_ANY, "Style:"), 0,
                           wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT)
        self.linestyle_choice = wx.Choice(self, wx.ID_ANY, 
                                          choices=[l.name for l in self.__available_lines])
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
        
        #line opacity
        line_alpha = mpl_lines[0].get_alpha()
        if not line_alpha:
            line_alpha = 1.0
        self.line_alpha_ctrl = floatspin.FloatSpin(self, -1,min_val=0.0, max_val=1.0,
                                                   value=line_alpha, increment=0.1, 
                                                   digits=1)
        self.line_alpha_txt = wx.StaticText(self, wx.ID_ANY, "Opacity:")
        
        line_ctrls_szr.Add(self.line_alpha_txt, 0,
                           wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT)
        line_ctrls_szr.Add(self.line_alpha_ctrl, 0 ,
                          wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT)
        
        floatspin.EVT_FLOATSPIN(self, self.line_alpha_ctrl.GetId(), self.on_line_alpha_change)
        
        
        #set the line selection to that of the data
        #it is possible that the line will have been set to something that
        #avoplot does not yet support - if so, default to None and issue warning
        if self.__line_symbol_to_idx_map.has_key(mpl_lines[0].get_linestyle()):
            #everything is fine
            current_line_idx = self.__line_symbol_to_idx_map[mpl_lines[0].get_linestyle()]
        else:
            current_line_idx = 0
            warnings.warn("Data series has an unsupported line style. "
                          "Defaulting to a line style of \'%s\' instead."%(self.__available_lines[0].name))
        
        #update the GUI appropriately for the current line selection
        self.linestyle_choice.SetSelection(current_line_idx)
        self.update_line_controls(self.__available_lines[current_line_idx])
        
        self.SetSizer(line_ctrls_szr)
        line_ctrls_szr.Fit(self)
        self.SetAutoLayout(True)
        self.parent.SendSizeEvent()
        self.parent.Refresh()
        
    
    def on_line_alpha_change(self, evnt):
        """
        Event handler for line opacity change events.
        """
        for l in self.mpl_lines:
            l.set_alpha(self.line_alpha_ctrl.GetValue())
        self.update_command()
    
        
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
        line_idx = self.__line_name_to_idx_map[evnt.GetString()]
        new_line = self.__available_lines[line_idx]
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
        self.line_alpha_ctrl.Show(current_line.has_width)
        self.line_alpha_txt.Show(current_line.has_width)
        self.line_weight_ctrl.Show(current_line.has_width)
        self.line_weight_ctrl_txt.Show(current_line.has_width)
        
        self.SendSizeEvent()
        self.parent.SendSizeEvent()
        self.Refresh()
        self.parent.Refresh()


class MarkerStyleEditorPanel(wx.Panel):
    
    def __init__(self, parent, mpl_lines, update_command, markers=all_available_markers):
        """
        Panel with controls to allow the user to change the markers used to plot
        a data series.
        """
        
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        
        self.__available_markers = markers
        self.parent = parent
        self.mpl_lines = mpl_lines
        self.update_command = update_command
        
        #build some mappings between marker properties and their indices in the list
        #of available markers
        self.__marker_symbol_to_idx_map = {}
        #self.__marker_name_to_idx_map = {}
        for i,m in enumerate(self.__available_markers):
            self.__marker_symbol_to_idx_map[m.mpl_symbol] = i
            #self.__marker_name_to_idx_map[m.name] = i

        marker_ctrls_szr = wx.FlexGridSizer(cols=2, vgap=5, hgap=2)
        
        #marker style
        #TODO - better way to include NullBitmap here (this is a quick hack for now)
        bitmaps = [wx.ArtProvider.GetBitmap(m.bitmap, size=wx.Size(16,16)) for m in self.__available_markers]
        
        self.marker_style_choice = widgets.BitmapChoice(self, choices=[""]*len(bitmaps), size=(80,-1),
                                                        style=wx.CB_READONLY, bitmaps=bitmaps)
        
        marker_ctrls_szr.Add(wx.StaticText(self, wx.ID_ANY, "Style:"), 0,
                             wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT)
        marker_ctrls_szr.Add(self.marker_style_choice, 0,
                             wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT)
        wx.EVT_COMBOBOX(self, self.marker_style_choice.GetId(), self.on_marker)
        
        #marker size
        self.marker_size_ctrl_txt = wx.StaticText(self, wx.ID_ANY, "Size:")
        self.marker_size_ctrl = floatspin.FloatSpin(self, wx.ID_ANY, min_val=0.1, max_val=50.0,
                                     value=mpl_lines[0].get_markersize(), increment=0.1, digits=2)
        marker_ctrls_szr.Add(self.marker_size_ctrl_txt, 0,
                           wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT)
        marker_ctrls_szr.Add(self.marker_size_ctrl, 0,
                           wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT)
        floatspin.EVT_FLOATSPIN(self, self.marker_size_ctrl.GetId(), self.on_markersize)
        
        #marker colour
        prev_col = matplotlib.colors.colorConverter.to_rgb(mpl_lines[0].get_markerfacecolor())
        prev_col = (255 * prev_col[0], 255 * prev_col[1], 255 * prev_col[2])
        self.marker_fillcolour_picker_txt = wx.StaticText(self, wx.ID_ANY, "Fill:")
        self.marker_fillcolour_picker = wx.ColourPickerCtrl(self, -1, prev_col)
        marker_ctrls_szr.Add(self.marker_fillcolour_picker_txt , 0,
                           wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT)
        marker_ctrls_szr.Add(self.marker_fillcolour_picker, 0 ,
                          wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT)
        wx.EVT_COLOURPICKER_CHANGED(self, self.marker_fillcolour_picker.GetId(), self.on_marker_fillcolour)

        #marker edge colour
        prev_col = matplotlib.colors.colorConverter.to_rgb(mpl_lines[0].get_markeredgecolor())
        prev_col = (255 * prev_col[0], 255 * prev_col[1], 255 * prev_col[2])
        self.marker_edgecolour_picker_txt = wx.StaticText(self, wx.ID_ANY, "Edge:")
        self.marker_edgecolour_picker = wx.ColourPickerCtrl(self, -1, prev_col)
        marker_ctrls_szr.Add(self.marker_edgecolour_picker_txt, 0,
                           wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT)
        marker_ctrls_szr.Add(self.marker_edgecolour_picker, 0 ,
                          wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT)
        wx.EVT_COLOURPICKER_CHANGED(self, self.marker_edgecolour_picker.GetId(), self.on_marker_edgecolour)        
        
        #marker edge width
        self.marker_edgewidth_ctrl_txt = wx.StaticText(self, wx.ID_ANY, "Edge width:")
        self.marker_edgewidth_ctrl = floatspin.FloatSpin(self, wx.ID_ANY, min_val=0.1, max_val=50.0,
                                     value=mpl_lines[0].get_markeredgewidth(), increment=0.1, digits=2)
        marker_ctrls_szr.Add(self.marker_edgewidth_ctrl_txt, 0,
                           wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT)
        marker_ctrls_szr.Add(self.marker_edgewidth_ctrl, 0,
                           wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT)
        floatspin.EVT_FLOATSPIN(self, self.marker_edgewidth_ctrl.GetId(), self.on_marker_edgewidth)
        
        #set the marker selection to that of the data
        #it is possible that the marker will have been set to something that
        #avoplot does not yet support - if so, default to None and issue warning
        if self.__marker_symbol_to_idx_map.has_key(mpl_lines[0].get_marker()):
            #everything is fine
            current_marker_idx = self.__marker_symbol_to_idx_map[mpl_lines[0].get_marker()]
        else:
            current_marker_idx = 0
            warnings.warn("Data series has an unsupported marker style. "
                          "Defaulting to a marker style of \'%s\' instead."%(self.__available_markers[0].name))
        
        #update the GUI appropriately for the current marker selection
        self.marker_style_choice.SetSelection(current_marker_idx)
        self.update_marker_controls(self.__available_markers[current_marker_idx])
        
        self.SetSizer(marker_ctrls_szr)
        marker_ctrls_szr.Fit(self)
        self.SetAutoLayout(True)
    
    
    def on_marker_fillcolour(self, evnt):
        """
        Event handler for marker fill colour change events
        """
        for l in self.mpl_lines:
            l.set_markerfacecolor(evnt.GetColour().GetAsString(wx.C2S_HTML_SYNTAX))
        self.update_command()
    
    
    def on_marker_edgecolour(self, evnt):
        """
        Event handler for marker fill colour change events
        """
        for l in self.mpl_lines:
            l.set_markeredgecolor(evnt.GetColour().GetAsString(wx.C2S_HTML_SYNTAX))
        self.update_command()
        
        
    def on_marker_edgewidth(self, evnt):
        """
        Event handler for line thickness change events.
        """
        for l in self.mpl_lines:
            l.set_markeredgewidth(self.marker_edgewidth_ctrl.GetValue())
        self.update_command()
            
            
    def on_marker(self, evnt):
        """
        Event handler for marker style change events.
        """
        marker_idx = evnt.GetSelection()
        new_marker = self.__available_markers[marker_idx]
        self.update_marker_controls(new_marker)
        for l in self.mpl_lines:
            l.set_marker(new_marker.mpl_symbol)
        self.update_command()
    
    
    def on_markersize(self, evnt):
        """
        Event handler for marker size change events
        """
        for l in self.mpl_lines:
            l.set_markersize(self.marker_size_ctrl.GetValue())
        self.update_command()
    
    
    def update_marker_controls(self, current_marker):
        """
        Shows or hides marker property controls depending on which are relevant
        for the currently selected marker type. current_marker should be a 
        MarkerType named tuple.
        """
        #show/hide the size controls
        self.marker_size_ctrl.Show(current_marker.has_size)
        self.marker_size_ctrl_txt.Show(current_marker.has_size)
        
        #show/hide the fill controls
        self.marker_fillcolour_picker.Show(current_marker.has_fill)
        self.marker_fillcolour_picker_txt.Show(current_marker.has_fill)
        
        #show/hide the edge controls
        self.marker_edgecolour_picker.Show(current_marker.has_edge)
        self.marker_edgecolour_picker_txt.Show(current_marker.has_edge)
        self.marker_edgewidth_ctrl.Show(current_marker.has_edge)
        self.marker_edgewidth_ctrl_txt.Show(current_marker.has_edge)
        
        self.SendSizeEvent()
        self.parent.SendSizeEvent()
        self.Refresh()
        self.parent.Refresh()
        
