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
import wx.combo
from avoplot.gui import text


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


class EditableCheckBox(wx.BoxSizer):
    
    def __init__(self, parent, label, edit_label='edit'):
        """
        A wx.Checkbox which displays a hyperlink next to it when checked. This
        should be subclassed and the on_checkbox and on_edit_link methods should
        be overridden to handle their respective events.
        """
        self.parent = parent
        
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)
        
        self.checkbox = wx.CheckBox(parent, -1, label+" ")
        self.edit_link = wx.HyperlinkCtrl(parent, wx.ID_ANY, edit_label, "",
                                          style=wx.HL_ALIGN_CENTRE|wx.BORDER_NONE)

        self.edit_link_parentheses = [wx.StaticText(parent, wx.ID_ANY, "("),
                                           wx.StaticText(parent, wx.ID_ANY, ")")]
        
        f = self.edit_link.GetFont()
        f.SetUnderlined(False)
        self.edit_link.SetFont(f)
        self.edit_link.SetVisitedColour(self.edit_link.GetNormalColour())
        
        #gridlines editing
        self.edit_link.Show(False)
        self.edit_link_parentheses[0].Show(False)
        self.edit_link_parentheses[1].Show(False)
        wx.EVT_HYPERLINK(parent, self.edit_link.GetId(), self.on_edit_link)
        
        self.Add(self.checkbox,0,wx.ALIGN_LEFT|wx.ALIGN_CENTRE_VERTICAL)
        self.Add(self.edit_link_parentheses[0],0,wx.ALIGN_LEFT|wx.ALIGN_CENTRE_VERTICAL|wx.RESERVE_SPACE_EVEN_IF_HIDDEN)
        self.Add(self.edit_link,0,wx.ALIGN_LEFT|wx.ALIGN_CENTRE_VERTICAL|wx.RESERVE_SPACE_EVEN_IF_HIDDEN)
        self.Add(self.edit_link_parentheses[1],0,wx.ALIGN_LEFT|wx.ALIGN_CENTRE_VERTICAL|wx.RESERVE_SPACE_EVEN_IF_HIDDEN)

        wx.EVT_CHECKBOX(parent, self.checkbox.GetId(), self._on_checkbox)
        
    
    def set_checked(self, value):
        """
        Sets the checkbox to be either checked (value = True), or unchecked 
        (value = False).
        """
        self.checkbox.SetValue(value)
        self.edit_link.Show(True)
        self.edit_link_parentheses[0].Show(True)
        self.edit_link_parentheses[1].Show(True)

    
    def _on_checkbox(self, evnt):
        """
        Event handler for the gridlines checkbox.
        """
        self.edit_link.Show(evnt.IsChecked())
        self.edit_link_parentheses[0].Show(evnt.IsChecked())
        self.edit_link_parentheses[1].Show(evnt.IsChecked())
        self.on_checkbox(evnt)   
    
    
    def on_checkbox(self, evnt):
        """
        Event handler for checkbox events. This should be overridden in the 
        subclass.
        """
        pass
            
            
    def on_edit_link(self, evnt):
        """
        Event handler for clicks on the hyperlink. This should be overridden in
        the subclass.
        """
        pass
        


class TextSetting(SettingBase, text.AnimatedText):
    """
    A text label next to a wx text entry control. The matplotlib Text object
    associated with the control is automatically animated to provide fast 
    redraws when the text is changed.
    
    A font properties button is displayed next to the text control (if the text
    entry box is not empty) which opens a font properties dialog.
    """
    def __init__(self, parent, label, text_obj):
        SettingBase.__init__(self, parent, label)
        text.AnimatedText.__init__(self, text_obj)
        self.text_obj = text_obj
        self.parent = parent
        self.mpl_figure = text_obj.get_figure()
        
        self.__bkgd_region = None
        
        self.tc = wx.TextCtrl(parent, -1, value=text_obj.get_text(), 
                              style=wx.TE_PROCESS_ENTER)
        wx.EVT_TEXT(parent, self.tc.GetId(), self.on_text_change)
        self.Add(self.tc, 1, wx.ALIGN_CENTRE_VERTICAL)
        
        prop_bmp = wx.ArtProvider.GetBitmap("avoplot_text_prop",wx.ART_BUTTON)
        self.prop_button = wx.BitmapButton(parent, wx.ID_ANY, prop_bmp)
        self.prop_button.SetToolTip(wx.ToolTip("Edit font properties"))
        self.Add(self.prop_button, 0, wx.ALIGN_CENTER_VERTICAL | 
                 wx.RESERVE_SPACE_EVEN_IF_HIDDEN)
        wx.EVT_BUTTON(parent, self.prop_button.GetId(), self.on_text_prop_button)
        
        wx.EVT_SET_FOCUS(self.tc,self.on_focus)
        wx.EVT_KILL_FOCUS(self.tc,self.on_unfocus)
        
        #hide the button if it is an empty string
        if not self.text_obj.get_text():
            self.prop_button.Show(False)
        
        
    def on_focus(self, evnt):
        """
        Event handler for when the control gets focus. Starts the text animation
        (i.e. caches the background).
        """
        self.start_text_animation()
        evnt.Skip()
    
    
    def on_unfocus(self, evnt):
        """
        Event handler for when the control loses focus. Stops the text animation
        """
        self.stop_text_animation()
        evnt.Skip()
    
    
    def on_text_change(self, evnt):
        """
        Event handler for text change events. Updates the text on the figure and
        redraws it.
        """
        self.text_obj.set_text(evnt.GetString())
        self.redraw_text()

        if evnt.GetString():
            if not self.prop_button.IsShown():
                self.prop_button.Show(True)
                
                #need to explicitly redraw the window area containing the button
                #otherwise it remains hidden (only a problem on Windows)
                self.parent.Refresh(rect=self.prop_button.GetRect())
        else:
            self.prop_button.Show(False)
    
    
    def on_text_prop_button(self, evnt):
        """
        Event handler for clicks on the "font properties" button. Opens a font
        properties dialog.
        """
        text.TextPropertiesEditor(self.parent, self.text_obj)


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
        
        

class BitmapChoice(wx.combo.OwnerDrawnComboBox):
    def __init__(self, parent, id=-1, value=wx.EmptyString, 
        pos=wx.DefaultPosition, size=wx.DefaultSize, 
        choices=[], style=0, validator=wx.DefaultValidator, name=wx.ComboBoxNameStr, bitmaps=[]):
        """
        BitmapChoice widget modified from the example posted by Torsten
        in this thread: http://markmail.org/thread/rb3c7377nuvnjfph
        """
        
        wx.combo.OwnerDrawnComboBox.__init__(self, parent, id, value, 
                pos, size, choices, style, validator, name )
                
        self.bitmaps = bitmaps[:]
                
    # Overridden from OwnerDrawnComboBox, called to draw each
    # item in the list
    def OnDrawItem(self, dc, rect, item, flags):
        if item == wx.NOT_FOUND:
            # painting the control, but there is no valid item selected yet
            return

        r = wx.Rect(*rect)  # make a copy
        #r.Deflate(3, 5)

        if flags & wx.combo.ODCB_PAINTING_CONTROL:
            # for painting the control itself
            dc.DrawBitmap( self.bitmaps[item], r.x+12, r.y+2, True)

        else:
            # for painting the items in the popup
            dc.DrawBitmap( self.bitmaps[item], r.x+12, r.y+2, True )
  
    # Overridden from OwnerDrawnComboBox, should return the height
    # needed to display an item in the popup, or -1 for default
    def OnMeasureItem(self, item):
        # Simply demonstrate the ability to have variable-height items
        return 20

    # Overridden from OwnerDrawnComboBox.  Callback for item width, or
    # -1 for default/undetermined
    def OnMeasureItemWidth(self, item):
        return 50; # default - will be measured from text width        
        