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
import sys
import matplotlib.text

class TextPropertiesEditor(wx.Dialog):
    """
    Dialog which allows the user to edit the text properties (colour, font etc.)
    of a matplotlib.text.Text object. The Text object to be edited should be 
    passed to the dialog constructor.
    """
    def __init__(self, parent, text_obj):

        if not isinstance(text_obj, matplotlib.text.Text):
            raise TypeError("Expecting matplotlib.text.Text instance"
                            ", got %s"%(type(text_obj)))
        self.main_text_obj = text_obj
        wx.Dialog.__init__(self, parent, wx.ID_ANY,"Text properties")
        vsizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        #set up the icon for the frame
        if sys.platform == "win32":
            self.SetIcon(wx.ArtProvider.GetIcon("avoplot", size=(16,16)))
        else:
            self.SetIcon(wx.ArtProvider.GetIcon("avoplot", size=(64,64)))
        
        #add the font properties panel
        self.font_props_panel = FontPropertiesPanel(self, text_obj)
        vsizer.Add(self.font_props_panel,0,wx.EXPAND)
        
        
        #create main buttons for editor frame
        self.ok_button = wx.Button(self, wx.ID_ANY, "Ok")
        self.apply_button = wx.Button(self, wx.ID_ANY, "Apply")
        self.cancel_button = wx.Button(self, wx.ID_ANY, "Cancel")
        button_sizer.Add(self.cancel_button, 0, wx.ALIGN_TOP | wx.ALIGN_RIGHT)
        button_sizer.Add(self.apply_button, 0, wx.ALIGN_TOP | wx.ALIGN_RIGHT)
        button_sizer.Add(self.ok_button, 0, wx.ALIGN_TOP | wx.ALIGN_RIGHT)
        vsizer.Add(button_sizer,0, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT)
        
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
                            ", got %s"%(type(text_obj)))
        
        #set the font
        text_obj.set_family(self.font_props_panel.get_font_name())
        
        #set font colour
        text_obj.set_color(self.font_props_panel.get_font_colour())
              
        #set font size
        text_obj.set_size(self.font_props_panel.get_font_size())
        
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
        
        #self.SetScrollRate(5,5)
        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        
        #create a list of available truetype fonts on this system
        self.avail_fonts = sorted(list(set([f.name for f in matplotlib.font_manager.fontManager.ttflist])))
        
        #create a font selection listbox
        self.font_selector = wx.ListBox(self, wx.ID_ANY, choices=self.avail_fonts)
        hsizer.Add(self.font_selector,1,wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.ALL, 
                   border=10)
        
        #set the initial font selection to that of the text object
        cur_font = text_obj.get_fontname()
        self.font_selector.SetSelection(self.avail_fonts.index(cur_font))
        
        #create a colour picker button
        colour_hsizer = wx.BoxSizer(wx.HORIZONTAL)
        text = wx.StaticText(self, -1, "Colour:")
        colour_hsizer.Add(text, 0, wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_LEFT)
        
        #set the colour picker's initial value to that of the text object
        prev_col = matplotlib.colors.colorConverter.to_rgb(text_obj.get_color())
        prev_col = (255 * prev_col[0], 255 * prev_col[1], 255 * prev_col[2])
        self.colour_picker = wx.ColourPickerCtrl(self, -1, prev_col)
        colour_hsizer.Add(self.colour_picker, 0 , 
                          wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT)
        vsizer.Add(colour_hsizer,0,  wx.ALIGN_RIGHT)
        
        #create a font size control
        size_hsizer = wx.BoxSizer(wx.HORIZONTAL)
        text = wx.StaticText(self, -1, "Size:")
        size_hsizer.Add(text, 0, wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_LEFT)

        self.size_ctrl = wx.SpinCtrl(self, wx.ID_ANY, min=4, max=100, 
                                     initial=text_obj.get_size())
        size_hsizer.Add(self.size_ctrl, 0 , wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_LEFT)
        vsizer.Add(size_hsizer,0, wx.ALIGN_RIGHT)
        
        
        hsizer.Add(vsizer,1,wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL,
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
    
       