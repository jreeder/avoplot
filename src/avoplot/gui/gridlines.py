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

from avoplot.gui import dialog, linestyle_editor



class GridPropertiesEditor(dialog.AvoPlotDialog):

    def __init__(self, parent, subplot, mpl_axis):
        """
        Dialog with controls to allow the user to edit gridline properties.
        """
        dialog.AvoPlotDialog.__init__(self, parent, "Gridline properties")
        
        #add line controls
        sbox = wx.StaticBox(self, wx.ID_ANY, 'Major Gridlines')
        line_ctrls_static_szr = wx.StaticBoxSizer(sbox, wx.VERTICAL)
             
        vsizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)     
        
        self.major_grid_panel = linestyle_editor.LineStyleEditorPanel(self, mpl_axis.get_gridlines(), subplot.update, linestyles=linestyle_editor.all_available_lines[1:])
        line_ctrls_static_szr.Add(self.major_grid_panel, 0, wx.ALIGN_TOP | wx.ALIGN_RIGHT)
        
        vsizer.Add(line_ctrls_static_szr,0,wx.EXPAND|wx.ALL, border=5)
        
        #create main buttons for editor frame
        self.ok_button = wx.Button(self, wx.ID_ANY, "Ok")
        button_sizer.Add(self.ok_button, 0, wx.ALIGN_TOP | wx.ALIGN_RIGHT)
        vsizer.Add(button_sizer, 0, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL, border=10)
        
        #register main button event callbacks
        wx.EVT_BUTTON(self, self.ok_button.GetId(), self.on_close)
        
        wx.EVT_CLOSE(self, self.on_close)
        self.SetSizer(vsizer)
        vsizer.SetMinSize((self.GetSize()[0],-1))
        
        vsizer.Fit(self)
        self.SetAutoLayout(True)
        
        self.CentreOnParent()
        self.ShowModal()
    
    
    def on_close(self, evnt):
        """
        Event handler for close events. Destroys the dialog box.
        """
        self.EndModal(wx.ID_OK)
        self.Destroy()
        
        