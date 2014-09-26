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

class AnimatedText:
    def __init__(self, text_objects):
        """
        Class to animate matplotlib.text.Text objects to allow fast editing of
        text properties. The general useage of the class is as follows:
        
        #create the animator passing it the text objects to be animated
        animator = AnimatedText([txt1, txt2])
        
        #start the animation - this caches the background and registers an event
        #handler to re-cache the background if it gets changed
        animator.start_text_animation()
        
        #make changes to the text here e.g.:
        txt1.set_color('r')
        
        #each time you want the changes to be drawn - call redraw_text()
        animator.redraw_text()
        
        #don't forget to end the animation when you are done with it!
        animator.stop_animation()
        """
        #if a single Text object has been passed, wrap in a list
        if isinstance(text_objects, matplotlib.text.Text):
            text_objects = [text_objects]
        
        for i,text_obj in enumerate(text_objects):
            if not isinstance(text_obj, matplotlib.text.Text):
                raise TypeError("At index %d: expecting matplotlib.text.Text instance"
                                ", got %s" % (i,type(text_obj)))
        
        #all the text objects must be in the same figure - it's hard to see why
        #this wouldn't be the case, but just in case
        figs = set([t.get_figure() for t in text_objects])
        assert len(figs) == 1, "All Text objects must be in the same Figure."
        
        self.__text_objects = text_objects
        self.__redraw_callback_id = None
        self.__bkgd_cache = None
        
        self.__mpl_fig = self.__text_objects[0].get_figure()
    
    
    def start_text_animation(self):
        """
        Start the animation of the text. This must be called before you call 
        redraw_text. This creates a cache of the figure background and registers
        a callback to update the cache if the background gets changed. 
        """
        
        #we have to protect against this method being called again
        #before the CallAfter call has completed 
        if self.__redraw_callback_id is None:
            self.__redraw_callback_id = -1
            wx.CallAfter(self.__start_text_animation)
    
    
    def __start_text_animation(self):
        self.__caching_in_progress = False
        
        #register a callback for draw events in the mpl canvas - if the canvas
        #has been redrawn then we need to re-cache the background region
        self.__redraw_callback_id = self.__mpl_fig.canvas.mpl_connect('draw_event', self.__cache_bkgd)
        
        #now cache the background region
        self.__cache_bkgd()
    
    
    def stop_text_animation(self):
        """
        Deletes the background cache and removes the update callback. Should be 
        called whenever you are finished animating the text
        """
        assert self.__redraw_callback_id is not None, ("stop_text_animation() "
                                                       "called before "
                                                       "start_text_animation()")
        
        #disconnect the event handler for canvas draw events
        self.__mpl_fig.canvas.mpl_disconnect(self.__redraw_callback_id)
        self.__redraw_callback_id = None
        
        #let the cached background get garbage collected
        self.__bkgd_cache = None
    
    
    def __cache_bkgd(self, *args):
        
        #This method is a bit of a hack! Since canvas.draw still renders some
        #matplotlib artists even if they are marked as animated, we instead 
        #set the alpha value of the artists to zero, then draw everything and
        #store the resulting canvas in a cache which can be used later to 
        #restore regions of the background. The *real* alpha values of the 
        #artists is then restored and the canvas is redrawn. This causes flicker
        #of the animated artists - but at least it seems to work.
        if self.__caching_in_progress:
            self.__caching_in_progress = False
            return
        
        self.__caching_in_progress = True
        
        #record the alpha values of the text objects so they can be restored
        prev_alphas = [t.get_alpha() for t in self.__text_objects]
        
        #hide the text objects by setting their alpha values to zero - note that 
        #using set_visible(False) instead leads to problems with layout.
        for t in self.__text_objects:
            t.set_alpha(0)
            
        self.__mpl_fig.canvas.draw()
        self.__bkgd_cache = self.__mpl_fig.canvas.copy_from_bbox(self.__mpl_fig.bbox)
        
        #now unhide the text by restoring its alpha value
        for i,t in enumerate(self.__text_objects):
            t.set_alpha(prev_alphas[i])
            self.__mpl_fig.draw_artist(t)
            
        self.__mpl_fig.canvas.blit(self.__mpl_fig.bbox)
         
    
    def redraw_text(self):
        """
        Restores the whole background region from the cache and then draws the 
        animated text objects over the top. You should call this every time you
        change the text and want the changes to be drawn to the screen.
        """
        assert self.__bkgd_cache is not None, ("redraw_text() called before "
                                               "__bkgd_cache was set. Have you "
                                               "called start_text_animation()?")
        
        #restore the whole figure background from the cached backgroud
        self.__mpl_fig.canvas.restore_region(self.__bkgd_cache)
        
        #now draw just the text objects (which have changed)
        for t in self.__text_objects:
            self.__mpl_fig.draw_artist(t)
        
        #blit the updated display to the screen  
        self.__mpl_fig.canvas.blit(self.__mpl_fig.bbox)
        
        

class TextPropertiesEditor(dialog.AvoPlotDialog):
    """
    Dialog which allows the user to edit the text properties (colour, font etc.)
    of a set of matplotlib.text.Text object. The Text objects to be edited should be 
    passed to the dialog constructor - which will accept either a single Text 
    object or an iterable of Text objects
    """
    def __init__(self, parent, text_objects):
        
        #if a single Text object has been passed, wrap in a list
        if isinstance(text_objects, matplotlib.text.Text):
            text_objects = [text_objects]
        
        for i,text_obj in enumerate(text_objects):
            if not isinstance(text_obj, matplotlib.text.Text):
                raise TypeError("At index %d: expecting matplotlib.text.Text instance"
                                ", got %s" % (i,type(text_obj)))
                
        self.__text_objects = text_objects
        dialog.AvoPlotDialog.__init__(self, parent, "Text properties")
        vsizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        #add the font properties panel
        self.font_props_panel = FontPropertiesPanel(self, text_objects)
        vsizer.Add(self.font_props_panel, 0, wx.EXPAND)
        
        #create main buttons for editor frame
        self.ok_button = wx.Button(self, wx.ID_ANY, "Ok")
        button_sizer.Add(self.ok_button, 0, wx.ALIGN_TOP | wx.ALIGN_RIGHT)
        vsizer.Add(button_sizer, 0, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL, border=10)
        
        #register main button event callbacks
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
        self.font_props_panel.Destroy()
        self.Destroy()
    
    
    def on_apply(self, evnt):
        """
        Event handler for Apply button clicks
        """
        for txt_obj in self.__text_objects:
            self.apply_to(txt_obj)
        
    
    def on_ok(self, evnt):
        """
        Event handler for Ok button clicks.
        """
        #self.apply_to(self.main_text_obj)
        self.EndModal(wx.ID_OK)
        self.font_props_panel.Destroy()
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
    
    Note that this panel does not use blitting methods to get fast text 
    animation because that causes layout problems for certain text objects - 
    e.g. the layout of axis labels and tick-labels are related to each other, 
    and this is not honoured properly if blitting methods are used. 
    """
    def __init__(self, parent, text_objects):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.__text_objects = text_objects
        self.mpl_figure = text_objects[0].get_figure()
        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer = wx.FlexGridSizer(cols=2, vgap=5)
        
        #create a list of available truetype fonts on this system
        self.avail_fonts = sorted(list(set([f.name for f in matplotlib.font_manager.fontManager.ttflist])))
        
        #create a font selection listbox
        self.font_selector = wx.ListBox(self, wx.ID_ANY, choices=self.avail_fonts)
        hsizer.Add(self.font_selector, 1, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.ALL,
                   border=10)
        
        #set the initial font selection to that of the text object
        cur_fonts = list(set([t.get_fontname() for t in text_objects]))
        if len(cur_fonts) == 1:
            self.font_selector.SetSelection(self.avail_fonts.index(cur_fonts[0]))
        
        #create a colour picker button
        text = wx.StaticText(self, -1, "Colour:  ")
        grid_sizer.Add(text, 0, wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT)
        
        wx.EVT_LISTBOX(self, self.font_selector.GetId(), self.on_font_selection)
        
        #set the colour picker's initial value to that of the text object
        prev_cols = [matplotlib.colors.colorConverter.to_rgb(t.get_color()) for t in text_objects]
        #TODO - what if the text objects have different colors
        prev_col = (255 * prev_cols[0][0], 255 * prev_cols[0][1], 255 * prev_cols[0][2])
        self.colour_picker = wx.ColourPickerCtrl(self, -1, prev_col)
        grid_sizer.Add(self.colour_picker, 0 ,
                          wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT)
        
        wx.EVT_COLOURPICKER_CHANGED(self, self.colour_picker.GetId(), self.on_font_colour)
        
        
        #create a font size control and set the initial value to that of the text
        text = wx.StaticText(self, -1, "Size:  ")
        grid_sizer.Add(text, 0, wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT)
        prev_size = [t.get_size() for t in text_objects][0]
        #TODO - what if the text objects have different sizes
        self.size_ctrl = wx.SpinCtrl(self, wx.ID_ANY, min=4, max=100,
                                     initial=prev_size)
        grid_sizer.Add(self.size_ctrl, 0 , wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT)
        
        wx.EVT_SPINCTRL(self, self.size_ctrl.GetId(), self.on_font_size)
        
        #create a drop-down box for specifying font weight       
        self.possible_weights = ['ultralight', 'light', 'normal', 'regular',
                                 'book', 'medium', 'roman', 'semibold',
                                 'demibold', 'demi', 'bold', 'heavy',
                                 'extra bold', 'black']

        text = wx.StaticText(self, -1, "Weight:  ")
        grid_sizer.Add(text, 0, wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT)

        self.weight_ctrl = wx.Choice(self, wx.ID_ANY, choices=self.possible_weights)
        
        grid_sizer.Add(self.weight_ctrl, 0, wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT)

        wx.EVT_CHOICE(self, self.weight_ctrl.GetId(), self.on_font_weight)
        
        #set the initial font weight selection to that of the text, this is a 
        #bit tricky since get_weight can return an integer or a string
        cur_weight = [t.get_weight() for t in text_objects][0]
        #TODO - what if the text objects have different weights
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
        
        wx.EVT_CHOICE(self, self.style_ctrl.GetId(), self.on_font_style)
        
        #set the initial font style selection to that of the text
        cur_style = [t.get_style() for t in text_objects][0]
        #TODO - what if the text objects have different styles
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
        
        wx.EVT_CHOICE(self, self.stretch_ctrl.GetId(), self.on_font_stretch)
        
        #set the initial font stretch selection to that of the text, this is a 
        #bit tricky since get_weight can return an integer or a string
        cur_stretch = [t.get_stretch() for t in text_objects][0]
        #TODO - what if the text objects have different stretches
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
    
    
    def redraw_text(self):
        """
        Redraws the text - does not use blitting for fast animation because that
        causes layout problems in some cases. 
        """
        self.mpl_figure.canvas.draw()
        
        
    def on_font_selection(self, evnt):
        """
        Event handler for font selection events.
        """
        new_font = evnt.GetString()
        for t in self.__text_objects:
            t.set_family(new_font)
        
        self.redraw_text()
    
    
    def on_font_colour(self, evnt):
        """
        Event handler for font colour change events.
        """
        new_colour = evnt.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
        for t in self.__text_objects:
            t.set_color(new_colour)
        
        self.redraw_text()
    
    
    def on_font_size(self, evnt):
        """
        Event handler for font size change events.
        """
        new_size = evnt.GetInt()
        for t in self.__text_objects:
            t.set_size(new_size)
        
        self.redraw_text()
    
    
    def on_font_weight(self, evnt):
        """
        Event handler for font weight (e.g. bold) change events.
        """
        new_weight = self.possible_weights[evnt.GetSelection()]
        for t in self.__text_objects:
            t.set_weight(new_weight)
        
        self.redraw_text()


    def on_font_style(self, evnt):
        """
        Event handler for font style (e.g. italic) change events.
        """
        new_style = evnt.GetString()
        for t in self.__text_objects:
            t.set_style(new_style)
        
        self.redraw_text()  
        
        
    def on_font_stretch(self, evnt):
        """
        Event handler for font stretch (e.g. compressed) change events.
        """
        new_stretch = evnt.GetString()
        for t in self.__text_objects:
            t.set_stretch(new_stretch)
        
        self.redraw_text()              
    
    
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
    
