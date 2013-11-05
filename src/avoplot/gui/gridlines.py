import wx
import matplotlib
import sys
import collections
from wx.lib.agw import floatspin 

from avoplot.gui import dialog

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


class GridPropertiesEditor(dialog.AvoPlotDialog):

    def __init__(self, parent, subplot, mpl_axis):
        
        dialog.AvoPlotDialog.__init__(self, parent, "Gridline properties")
        
        vsizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        
        self.major_grid_panel = GridlineEditorPanel(self, mpl_axis)
        vsizer.Add(self.major_grid_panel,1,wx.EXPAND)
        
        #create main buttons for editor frame
        self.ok_button = wx.Button(self, wx.ID_ANY, "Ok")
        button_sizer.Add(self.ok_button, 0, wx.ALIGN_TOP | wx.ALIGN_RIGHT)
        vsizer.Add(button_sizer, 0, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT)
        
        #register main button event callbacks
        wx.EVT_BUTTON(self, self.ok_button.GetId(), self.on_close)
        
        wx.EVT_CLOSE(self, self.on_close)
        self.SetSizer(vsizer)
        vsizer.Fit(self)
        self.SetAutoLayout(True)
        
        self.CentreOnParent()
        self.ShowModal()
    
    def on_close(self, evnt):
        self.EndModal(wx.ID_OK)
        self.Destroy()
        
        


class GridlineEditorPanel(wx.Panel): 
    
    def __init__(self, parent, mpl_axis):       
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        
        mpl_lines = mpl_axis.get_gridlines()
        
        #add line controls
        line_ctrls_static_szr = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, 'Major Gridlines'), wx.VERTICAL)
        
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
        
        
        line_ctrls_static_szr.Add(line_ctrls_szr, 0, wx.ALIGN_RIGHT)
        
        self.SetSizer(line_ctrls_static_szr)
        line_ctrls_static_szr.Fit(self)
        self.SetAutoLayout(True)
        
    def on_linestyle(self, evnt):
        pass
    
    def on_linewidth(self, evnt):
        pass
    
    def on_line_colour_change(self, evnt):
        pass