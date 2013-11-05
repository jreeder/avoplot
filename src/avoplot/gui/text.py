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
The text module contains classes and functions for editing matplotlib Text 
objects
"""

import wx
import matplotlib.text

from avoplot.gui import dialog

class TextPropertiesEditor(dialog.AvoPlotDialog):
    """
    Dialog which allows the user to edit the text properties (colour, font etc.)
    of a matplotlib.text.Text object. The Text object to be edited should be 
    passed to the dialog constructor.
    """
    def __init__(self, parent, text_obj):

        if not isinstance(text_obj, matplotlib.text.Text):
            raise TypeError("Expecting matplotlib.text.Text instance"
                            ", got %s" % (type(text_obj)))
        self.main_text_obj = text_obj
        dialog.AvoPlotDialog.__init__(self, parent, "Text properties")
        vsizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        #add the font properties panel
        self.font_props_panel = FontPropertiesPanel(self, text_obj)
        vsizer.Add(self.font_props_panel, 0, wx.EXPAND)
        
        #create main buttons for editor frame
        self.ok_button = wx.Button(self, wx.ID_ANY, "Ok")
        self.apply_button = wx.Button(self, wx.ID_ANY, "Apply")
        self.cancel_button = wx.Button(self, wx.ID_ANY, "Cancel")
        button_sizer.Add(self.cancel_button, 0, wx.ALIGN_TOP | wx.ALIGN_RIGHT)
        button_sizer.AddSpacer(5)
        button_sizer.Add(self.apply_button, 0, wx.ALIGN_TOP | wx.ALIGN_RIGHT)
        button_sizer.AddSpacer(5)
        button_sizer.Add(self.ok_button, 0, wx.ALIGN_TOP | wx.ALIGN_RIGHT)
        vsizer.Add(button_sizer, 0, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL, border=10)
        
        #register main button event callbacks
        wx.EVT_BUTTON(self, self.cancel_button.GetId(), self.on_close)
        wx.EVT_BUTTON(self, self.apply_button.GetId(), self.on_apply)
        wx.EVT_BUTTON(self, self.ok_button.GetId(), self.on_ok)
        
        wx.EVT_CLOSE(self, self.on_close)
        self.SetSizer(vsizer)
        vsizer.Fit(self)
        self.SetAutoLayout(True)
        
        self.CentreOnParent()
        self.ShowModal()
        
        
    def on_close(self, evnt):
        """
        Event handler for frame close events
        """
        self.EndModal(wx.ID_CANCEL)
        self.Destroy()
    
    
    def on_apply(self, evnt):
        """
        Event handler for Apply button clicks
        """
        self.apply_to(self.main_text_obj)
        
    
    def on_ok(self, evnt):
        """
        Event handler for Ok button clicks.
        """
        self.apply_to(self.main_text_obj)
        self.EndModal(wx.ID_OK)
        self.Destroy()
        
        
    def apply_to(self, text_obj):
        """
        Applies the selected properties to text_obj which must be a 
        matplotlib.text.Text object
        """
        
        if not isinstance(text_obj, matplotlib.text.Text):
            raise TypeError("Expecting matplotlib.text.Text instance"
                            ", got %s" % (type(text_obj)))
        
        #set the font
        text_obj.set_family(self.font_props_panel.get_font_name())
        
        #set font colour
        text_obj.set_color(self.font_props_panel.get_font_colour())
              
        #set font size
        text_obj.set_size(self.font_props_panel.get_font_size())
        
        #set the weight
        text_obj.set_weight(self.font_props_panel.get_font_weight())
        
        #set the style
        text_obj.set_style(self.font_props_panel.get_font_style())
        
        #set the font stretch
        text_obj.set_stretch(self.font_props_panel.get_font_stretch())
        
        #update the display
        text_obj.figure.canvas.draw()



class FontPropertiesPanel(wx.Panel):
    """
    Panel to hold the text property editing controls within the 
    TextPropertiesEditor dialog. The Text object to be edited should be passed
    to the constructor.
    """
    def __init__(self, parent, text_obj):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer = wx.FlexGridSizer(5, 2, vgap=5)
        
        #create a list of available truetype fonts on this system
        self.avail_fonts = sorted(list(set([f.name for f in matplotlib.font_manager.fontManager.ttflist])))
        
        #create a font selection listbox
        self.font_selector = wx.ListBox(self, wx.ID_ANY, choices=self.avail_fonts)
        hsizer.Add(self.font_selector, 1, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.ALL,
                   border=10)
        
        #set the initial font selection to that of the text object
        cur_font = text_obj.get_fontname()
        self.font_selector.SetSelection(self.avail_fonts.index(cur_font))
        
        #create a colour picker button
        text = wx.StaticText(self, -1, "Colour:  ")
        grid_sizer.Add(text, 0, wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT)
        
        #set the colour picker's initial value to that of the text object
        prev_col = matplotlib.colors.colorConverter.to_rgb(text_obj.get_color())
        prev_col = (255 * prev_col[0], 255 * prev_col[1], 255 * prev_col[2])
        self.colour_picker = wx.ColourPickerCtrl(self, -1, prev_col)
        grid_sizer.Add(self.colour_picker, 0 ,
                          wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT)
        
        
        #create a font size control and set the initial value to that of the text
        text = wx.StaticText(self, -1, "Size:  ")
        grid_sizer.Add(text, 0, wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT)

        self.size_ctrl = wx.SpinCtrl(self, wx.ID_ANY, min=4, max=100,
                                     initial=text_obj.get_size())
        grid_sizer.Add(self.size_ctrl, 0 , wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT)
        
        
        #create a drop-down box for specifying font weight       
        self.possible_weights = ['ultralight', 'light', 'normal', 'regular',
                                 'book', 'medium', 'roman', 'semibold',
                                 'demibold', 'demi', 'bold', 'heavy',
                                 'extra bold', 'black']

        text = wx.StaticText(self, -1, "Weight:  ")
        grid_sizer.Add(text, 0, wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT)

        self.weight_ctrl = wx.Choice(self, wx.ID_ANY, choices=self.possible_weights)
        
        grid_sizer.Add(self.weight_ctrl, 0, wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT)

        
        #set the initial font weight selection to that of the text, this is a 
        #bit tricky since get_weight can return an integer or a string
        cur_weight = text_obj.get_weight()
        if not type(cur_weight) is str:
            idx = int(round(cur_weight / 1000.0 * len(self.possible_weights), 0))
        else:
            idx = self.possible_weights.index(cur_weight)
        self.weight_ctrl.SetSelection(idx)
        
        
        #create a drop down box for specifying font style
        self.possible_styles = ['normal', 'italic', 'oblique']

        text = wx.StaticText(self, -1, "Style:  ")
        grid_sizer.Add(text, 0, wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT)

        self.style_ctrl = wx.Choice(self, wx.ID_ANY, choices=self.possible_styles)
        
        grid_sizer.Add(self.style_ctrl, 0 , wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT)
        
        
        #set the initial font style selection to that of the text
        cur_style = text_obj.get_style()
        idx = self.possible_styles.index(cur_style)
        self.style_ctrl.SetSelection(idx)    
        
        #create a drop down box for selecting font stretch
        self.possible_stretches = ['ultra-condensed', 'extra-condensed',
                                 'condensed', 'semi-condensed', 'normal',
                                 'semi-expanded', 'expanded', 'extra-expanded',
                                 'ultra-expanded']
        
        text = wx.StaticText(self, -1, "Stretch:  ")
        grid_sizer.Add(text, 0, wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT)

        self.stretch_ctrl = wx.Choice(self, wx.ID_ANY, choices=self.possible_stretches)
        
        grid_sizer.Add(self.stretch_ctrl, 0 , wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT)

        
        #set the initial font stretch selection to that of the text, this is a 
        #bit tricky since get_weight can return an integer or a string
        cur_stretch = text_obj.get_stretch()
        if not type(cur_stretch) is str:
            idx = int(round(cur_stretch / 1000.0 * len(self.possible_stretches), 0))
        else:
            idx = self.possible_stretches.index(cur_stretch)
        self.stretch_ctrl.SetSelection(idx)
        
        
        hsizer.Add(grid_sizer, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.ALL,
                   border=10)
        
        self.SetSizer(hsizer)
        hsizer.Fit(self)
        self.SetAutoLayout(True)
    
    
    def get_font_colour(self):
        """
        Returns the currently selected font colour (as a HTML string).
        """
        return self.colour_picker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
    
    
    def get_font_size(self):
        """
        Returns the currently selected font size (integer number of points)
        """
        return self.size_ctrl.GetValue() 
    
    
    def get_font_name(self):
        """
        Returns the name of the currently selected font.
        """
        return self.avail_fonts[self.font_selector.GetSelection()]
    
    
    def get_font_weight(self):
        """
        Returns the weight of the font currently selected
        """
        return self.possible_weights[self.weight_ctrl.GetSelection()]
    
    
    def get_font_style(self):
        """
        Returns the style ('normal', 'italic' etc.) of the font currently 
        selected
        """
        return self.possible_styles[self.style_ctrl.GetSelection()]
    
    
    def get_font_stretch(self):
        """
        Returns the stretch of the font currently selected
        """
        return self.possible_stretches[self.stretch_ctrl.GetSelection()]
    
