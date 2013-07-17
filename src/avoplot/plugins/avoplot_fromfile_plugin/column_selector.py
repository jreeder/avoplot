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
import re
import wx.lib.buttons
import wx.grid
import numpy
import os
import avoplot
#from avoplot.gui.plots import PlotPanelBase
from avoplot.series import XYDataSeries

class InvalidSelectionError(ValueError):
    pass

class FileContentsPanel(wx.Panel):
    def __init__(self, parent, file_contents):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        box = wx.StaticBox(self, wx.ID_ANY, "File Contents")
        vsizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        #create the rows/columns check boxes for selecting data format
        self.cols_checkbox = wx.CheckBox(self, wx.ID_ANY, "Columns")
        self.rows_checkbox = wx.CheckBox(self, wx.ID_ANY, "Rows")
        chkbox_sizer = wx.BoxSizer(wx.HORIZONTAL)
        chkbox_sizer.Add(wx.StaticText(self, wx.ID_ANY, "Data is in:"), 0,
                         wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        chkbox_sizer.Add(self.cols_checkbox, 0
                         , wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        chkbox_sizer.Add(self.rows_checkbox, 0,
                         wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        self.cols_checkbox.SetValue(True)
        
        wx.EVT_CHECKBOX(self, self.cols_checkbox.GetId(), self.on_cols_chkbox)
        wx.EVT_CHECKBOX(self, self.rows_checkbox.GetId(), self.on_rows_chkbox)
        
        vsizer.Add(chkbox_sizer, 0, wx.ALIGN_LEFT | wx.ALL, border=5)
        
        #add a drop-down panel for displaying the file header contents (if there is any)
        if file_contents.header:
            self.header_pane = wx.CollapsiblePane(self, wx.ID_ANY, "File Header")
            win = self.header_pane.GetPane()
            header_txt_ctrl = wx.TextCtrl(win, wx.ID_ANY, value=file_contents.header,
                                          style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
            
            header_pane_sizer = wx.BoxSizer(wx.VERTICAL)
            header_pane_sizer.Add(header_txt_ctrl, 1, wx.GROW | wx.ALL, border=5)
            
            win.SetSizer(header_pane_sizer)
            header_pane_sizer.SetSizeHints(win)
            wx.EVT_COLLAPSIBLEPANE_CHANGED(self, self.header_pane.GetId(), self.on_expand)
            
            vsizer.Add(self.header_pane, 0, wx.GROW)
        else:
            self.header_pane = None
        
        
        #add the grid panel for data selection
        self.grid_panel = ColumnDataPanel(self, file_contents)
        vsizer.Add(self.grid_panel, 1, wx.EXPAND)

        #add a drop-down panel for displaying the file footer contents (if there is any)
        if file_contents.footer:
            self.footer_pane = wx.CollapsiblePane(self, wx.ID_ANY, "File Footer")
            win = self.footer_pane.GetPane()
            footer_txt_ctrl = wx.TextCtrl(win, wx.ID_ANY, value=file_contents.footer,
                                          style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
            
            footer_pane_sizer = wx.BoxSizer(wx.VERTICAL)
            footer_pane_sizer.Add(footer_txt_ctrl, 1, wx.GROW | wx.ALL, border=5)
            
            win.SetSizer(footer_pane_sizer)
            footer_pane_sizer.SetSizeHints(win)
            wx.EVT_COLLAPSIBLEPANE_CHANGED(self, self.footer_pane.GetId(), self.on_expand)
            
            vsizer.Add(self.footer_pane, 0, wx.GROW)
        else:
            self.footer_pane = None
        self.SetSizer(vsizer)
        vsizer.Fit(self)
        self.SetAutoLayout(True)
    
    def on_expand(self, evnt):
        self.SendSizeEvent()
    
    def on_cols_chkbox(self, evnt):
        status = self.cols_checkbox.IsChecked()
        self.rows_checkbox.SetValue(not status)
 
    def on_rows_chkbox(self, evnt):
        status = self.rows_checkbox.IsChecked()
        self.cols_checkbox.SetValue(not status)
    
    
    def enable_select_mode(self, val, data_series):
        self.grid_panel.enable_select_mode(val, data_series)
        
        if val:
            self.cols_checkbox.Disable()
            self.rows_checkbox.Disable()
            if self.header_pane is not None:
                self.header_pane.Disable()
            if self.footer_pane is not None:
                self.footer_pane.Disable()
        else:
            self.cols_checkbox.Enable()
            self.rows_checkbox.Enable()
            if self.header_pane is not None:
                self.header_pane.Enable()
            if self.footer_pane is not None:
                self.footer_pane.Enable()


class ColumnDataPanel(wx.ScrolledWindow):
    def __init__(self, parent, file_contents):
        wx.ScrolledWindow.__init__(self, parent, wx.ID_ANY)
        self.SetScrollRate(5,5)
        self.file_contents = file_contents
        n_cols = file_contents.get_number_of_columns()
        n_rows = file_contents.get_number_of_rows()
        
        vsizer = wx.BoxSizer(wx.VERTICAL)
     
        #create cells
        self.grid = wx.grid.Grid(self, wx.ID_ANY)
        self.grid.EnableGridLines(False)
        self.grid.CreateGrid(n_rows, n_cols)
        self.col_letter_names = []
                
        for c, col in enumerate(file_contents.get_columns()):
            self.col_letter_names.append(self.grid.GetColLabelValue(c))
            if col.title and not col.title.isspace():
                self.grid.SetColLabelValue(c, ''.join([self.grid.GetColLabelValue(c),'\n',col.title]))
            
            for r, data in enumerate(col.raw_data):
                self.grid.SetCellValue(r, c, data)
        
        self.grid.AutoSize()
        
        #set the size of the grid to be big enough that the grid's scrollbars are
        #not enabled
        #TODO - this will break if you resize some of the cells
        self.grid.SetSize(self.grid.GetBestVirtualSize())
        
        
        #create choice boxes for data types
        self.data_type_sizer = wx.BoxSizer(wx.HORIZONTAL)
        text = wx.StaticText(self, wx.ID_ANY,"Data type:")
        self.data_type_sizer.Add(text,0,wx.ALIGN_LEFT| wx.ALIGN_CENTER_VERTICAL)
        self.data_type_sizer.AddSpacer(self.grid.GetRowLabelSize()-text.GetSize()[0])
        self.data_type_choices = []
        for col in file_contents.get_columns():
            choice = wx.Choice(self, wx.ID_ANY,choices=["Float", "String"])
            self.data_type_choices.append(choice)
            self.data_type_sizer.Add(choice,0,wx.ALIGN_CENTER_VERTICAL|wx.GROW)
                
        #match the data type choice box sizes to the grid column sizes
        for idx in range(len(self.data_type_choices)):
            choice_size = self.data_type_choices[idx].GetSize()[0]
            col_size = self.grid.GetColSize(idx)
            
            if choice_size < col_size:
                self.data_type_choices[idx].SetMinSize((col_size,-1))
            else:
                self.grid.SetColSize(idx,choice_size)
                self.grid.SetColMinimalWidth(idx,choice_size)
        wx.grid.EVT_GRID_CMD_COL_SIZE(self, self.grid.GetId(), self.on_column_resize)
        
        vsizer.Add(self.data_type_sizer, 0, wx.EXPAND)
        vsizer.Add(self.grid, 1, wx.EXPAND)
        
        self.SetSizer(vsizer)
        vsizer.Fit(self)
        
        #self.grid.EnableGridLines(True)

    
    def get_selection(self):
        """
        Returns a tuple (selection string, col_idx, data mask) where selection string is 
        a human readable string of the selection made, col_idx is the index of the column that the mask relates to and data mask is a numpy 
        mask array where True indicates a selection and False indicates a value to
        mask out.
        """
        
        cols_selected = self.grid.GetSelectedCols()
        cells_selected = self.grid.GetSelectedCells()
        blocks_TL_selected = self.grid.GetSelectionBlockTopLeft()
        blocks_BR_selected = self.grid.GetSelectionBlockBottomRight()
        
        if cols_selected:
            #only complete columns have been selected (or at least if other cells have also been
            #selected then they are invalid)
            if (len(cols_selected) > 1 or blocks_TL_selected or cells_selected):
                raise InvalidSelectionError("You cannot select data from more than one column for an axis data series.")

            selection_str = '%s[:]'%self.file_contents.get_col_name(cols_selected[0])
            return selection_str
        
        if not (cells_selected or blocks_BR_selected):
            #No selection made
            return ""
        
        #otherwise we have a selection of blocks of cells and individual cells to sort out       
        #first check that they are all from the same column
        cols = set([c for r,c in cells_selected] + [c for r,c in blocks_TL_selected] + 
                   [c for r,c in blocks_BR_selected])
        
        if len(cols) != 1:
            raise InvalidSelectionError("You cannot select data from more than one column for an axis data series.")
        
        col_idx = cols.pop()
        
        #create a list of (start_row, end_row) tuples for all the cells and blocks selected
        start_idxs = [r for r,c in blocks_TL_selected] + [r for r,c in cells_selected]
        end_idxs = [r for r,c in blocks_BR_selected] + [r for r,c in cells_selected]       
        selections = zip(start_idxs, end_idxs)
        
        #sort them into row order
        tuple_compare = lambda x1,x2: cmp(x1[0], x2[0])
        selections.sort(cmp=tuple_compare)
        
        #we +1 to the row numbers because numbering starts at 1 for the row labels but at 0
        #for their indices
        selection_str = ', '.join(['%s[%d:%d]'%(self.col_letter_names[col_idx], 
                                                start+1, end+1) for start,end in selections])
        
        return selection_str
        
            
                
    def enable_select_mode(self, val, data_series):
        self.set_editable(not val)
        if val:
            #self.grid.GetGridWindow().SetCursor(wx.StockCursor(wx.CURSOR_CROSS))
            self.grid.ClearSelection()
            for choice in self.data_type_choices:
                choice.Disable()
        else:
            #self.grid.GetGridWindow().SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
            for choice in self.data_type_choices:
                choice.Enable()
            try:
                selection = self.get_selection()
            except InvalidSelectionError,e:
                wx.MessageBox(e.args[0], "AvoPlot", wx.ICON_EXCLAMATION)
                selection = ""
            data_series.set_selection(selection)
        
        
    def set_editable(self, value):
        self.grid.EnableDragGridSize(value)  
        self.grid.EnableDragColSize(value)
        self.grid.EnableDragRowSize(value)
        self.grid.EnableEditing(value)

    
    def on_column_resize(self, evnt):
        """
        Handle column resize events - this requires all the data_type choices
        to be resized to match the columns
        """
        for idx in range(len(self.data_type_choices)):
            col_size = self.grid.GetColSize(idx)
            self.data_type_choices[idx].SetMinSize((col_size,-1))
        
        self.data_type_sizer.Layout()
     
   
class XYDataSeriesPanel(wx.Panel):
    def __init__(self, parent, file_contents, main_frame):
        self.__selecting_x = False
        self.file_contents = file_contents        
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.main_frame = main_frame
        
        self.xseries_box = wx.TextCtrl(self, wx.ID_ANY)
        self.yseries_box = wx.TextCtrl(self, wx.ID_ANY)
        button_sz = self.yseries_box.GetSize()[1]
        self.add_button = wx.BitmapButton(self, wx.ID_ANY, wx.ArtProvider.GetBitmap("avoplot_add",wx.ART_BUTTON))
        self.remove_button = wx.BitmapButton(self, wx.ID_ANY, wx.ArtProvider.GetBitmap("avoplot_remove",wx.ART_BUTTON))
        
        self.select_x_button = wx.lib.buttons.ThemedGenBitmapToggleButton(self, wx.ID_ANY, wx.ArtProvider.GetBitmap("avoplot_col_select",wx.ART_BUTTON), size=(button_sz,button_sz))
        self.select_y_button = wx.lib.buttons.ThemedGenBitmapToggleButton(self, wx.ID_ANY, wx.ArtProvider.GetBitmap("avoplot_col_select",wx.ART_BUTTON), size=(button_sz,button_sz))
        wx.EVT_BUTTON(self, self.select_x_button.GetId(), self.on_select_x_series)
        wx.EVT_BUTTON(self, self.select_y_button.GetId(), self.on_select_y_series)
        
        self.hsizer.Add(wx.StaticText(self, wx.ID_ANY, "x data: "),0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT)
        self.hsizer.Add(self.xseries_box, 1, wx.ALIGN_CENTER_VERTICAL| wx.ALIGN_LEFT)
        self.hsizer.Add(self.select_x_button,0,wx.ALIGN_CENTER_VERTICAL| wx.ALIGN_LEFT)
        self.hsizer.AddSpacer(10)
        
        self.hsizer.Add(wx.StaticText(self, wx.ID_ANY, "y data: "),0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT)
        self.hsizer.Add(self.yseries_box, 1, wx.ALIGN_CENTER_VERTICAL| wx.ALIGN_LEFT)
        self.hsizer.Add(self.select_y_button,0,wx.ALIGN_CENTER_VERTICAL| wx.ALIGN_LEFT)
        self.hsizer.AddSpacer(10)
        
        self.hsizer.Add(self.remove_button,0, wx.ALIGN_CENTER_VERTICAL| wx.ALIGN_LEFT| wx.RESERVE_SPACE_EVEN_IF_HIDDEN)
        self.hsizer.Add(self.add_button,0, wx.ALIGN_CENTER_VERTICAL| wx.ALIGN_LEFT| wx.RESERVE_SPACE_EVEN_IF_HIDDEN)      
        
        self.SetSizer(self.hsizer)
        self.hsizer.Fit(self)
        self.SetAutoLayout(True)

    
    def enable_select_mode(self, val, series):
        if val:
            self.xseries_box.Disable()
            self.yseries_box.Disable()
            self.select_x_button.Disable()
            self.select_y_button.Disable()
            self.add_button.Disable()
            self.remove_button.Disable()
        else:
            self.xseries_box.Enable()
            self.yseries_box.Enable()
            self.select_x_button.Enable()
            self.select_y_button.Enable()
            self.add_button.Enable()
            self.remove_button.Enable()
            
    
    def plot_into_axes(self, axes):
        
        xdata = self.get_x_series_data()
        ydata = self.get_y_series_data()
        
        if xdata is None and ydata is None:
            return
        
        if xdata is None:
            axes.plot(numpy.arange(len(ydata)),ydata)
        elif ydata is None:
            axes.plot(xdata,numpy.arange(len(xdata)))
        else:
             
             #this stuff is redundant for now since the masked arrays will always have
             #the same length
#            #if the data has different lengths then only plot
#            #the overlapping regions
#            if len(xdata) != len(ydata):
#                d = wx.MessageDialog(self, "Your x and y data series have different lengths."
#                                 "Plot the overlapping region?", "AvoPlot")
#                if d.ShowModal() == wx.ID_CANCEL:
#                    return
#                
#                if len(xdata) > len(ydata):
#                    axes.plot(xdata[:len(ydata)], ydata)
#                else:
#                    axes.plot(xdata, ydata[:len(xdata)])
#            else:
                axes.plot(xdata, ydata)
    
    
    def get_series_data(self):
        """
        Returns a tuple of (xdata, ydata)
        """
        xdata = self.get_x_series_data()
        ydata = self.get_y_series_data()
        
        if xdata is None and ydata is None:
            return
        
        if xdata is None:
            return (numpy.arange(len(ydata)),ydata)
        elif ydata is None:
            return (xdata,numpy.arange(len(xdata)))
        else:
            return (xdata, ydata)
        
        
    def get_x_series_data(self):
        return self.__get_data_selection(self.xseries_box.GetValue(), False)      
        
    def get_y_series_data(self):
        return self.__get_data_selection(self.yseries_box.GetValue(), False)     
    
    def validate_selection(self, row_selection):
        self._validate_selection_str(self.xseries_box.GetValue(), row_selection)
        self._validate_selection_str(self.yseries_box.GetValue(), row_selection)
      
    def _validate_selection_str(self, selection_str, row_selection=False):
        if row_selection:
            raise NotImplementedError("Selecting rows as data series is not implemented yet!")
        
        if not selection_str or selection_str.isspace():
            return []
        
        selection_blocks = selection_str.split(',')
        
        if row_selection:
            raise NotImplementedError("Selecting rows as data series is not implemented yet!")
        else:
                   
            regexp = re.compile(r'''
                                   (?:^\s*(?P<column>[A-Z]+) #matches column name 
                                   \s*\[\s*(?P<lower_bound>[0-9]*) #matches lower bound number (if there is one)
                                   \s*:\s*  
                                   (?P<upper_bound>[0-9]*)\s*\]\s*$) #matches upped bound number (if there is one)''', 
                                   flags=re.VERBOSE)
            cols = set()
            selection_params = []
            for block in selection_blocks:
                match = regexp.match(block)
                
                if match is None:
                    #then there is a syntax error in the selection string
                    raise InvalidSelectionError("Syntax error in selection string. \'%s\' is not a valid selection, expecting something of the form \'A[2:8]\'."%block)
            
                params = match.groupdict()
                selection_params.append(params)

                cols.add(params['column'])
                n_rows = self.file_contents.get_column_by_name(params['column']).get_number_of_rows()
                   
                if not params['lower_bound']:
                    params['lower_bound'] = '1'
                if not params['upper_bound']:
                    params['upper_bound'] = str(n_rows)
                
                lower_bound = int(params['lower_bound'])
                upper_bound = int(params['upper_bound'])
                
                if lower_bound < 1:
                    raise InvalidSelectionError("Value error in selection string. \'%s\' is not a valid selection, lower bound must be greater than zero."%block)
                
                if lower_bound > upper_bound:
                    raise InvalidSelectionError("Value error in selection string. \'%s\' is not a valid selection, upper bound cannot be smaller than lower bound."%block)
                 
                if upper_bound > n_rows:
                    raise InvalidSelectionError("Value error in selection string. \'%s\' is not a valid selection, upper bound is outside data range."%block)
        
            if len(cols) != 1:
                raise InvalidSelectionError("Selection cannot contain data from multiple columns.")
            
        return selection_params
                    
    def __get_data_selection(self, selection_str, row_selection=False):
        """
        Given a selection string (of the form "A[1:20], A[23:25]", returns a masked array
        of the requested data.
        """
        if row_selection:
            raise NotImplementedError("Selecting rows as data series is not implemented yet!")
        
        if not selection_str or selection_str.isspace():
            #empty string - no selection made
            return None
        
        selection_params = self._validate_selection_str(selection_str, row_selection)
        
        #see if we have any complete column selections - life is easy if we do!
        blocks = []
        for s in selection_params:
            #-1 because array indexing starts at 0 but row indexing starts at 1
            blocks.append((int(s['lower_bound'])-1,int(s['upper_bound'])-1))
        
        #otherwise build a mask for the selection       
        column = self.file_contents.get_column_by_name(selection_params[0]['column'])
        data_mask = column.get_data_mask()
        
        #sort selection blocks into row order
        tuple_compare = lambda x1,x2: cmp(x1[0], x2[0])
        blocks.sort(cmp=tuple_compare)

        selection_mask = numpy.zeros_like(data_mask)
        
        for start,end in blocks:
            selection_mask[start:end+1] = True
        mask = numpy.logical_and(data_mask, selection_mask)
        
        return numpy.ma.masked_array(column.get_data(), mask=numpy.logical_not(mask))
        

          
    def get_add_button_id(self):
        return self.add_button.GetId()
    
    
    def get_remove_button_id(self):
        return self.remove_button.GetId()
    
    
    def set_button_visibility(self, add_button, remove_button):
        self.add_button.Show(add_button)
        self.remove_button.Show(remove_button)
        self.hsizer.Layout()
    
    
    def on_select_x_series(self, evnt):
        if self.select_x_button.GetToggle():
            self.__selecting_x = True            
            self.main_frame.enable_select_mode(True, self)
            self.select_x_button.Enable()
        else:
            self.main_frame.enable_select_mode(False, self)
            self.__selecting_x = False
            
    
    
    def on_select_y_series(self, evnt):
        if self.select_y_button.GetToggle():
            self.__selecting_x = False        
            self.main_frame.enable_select_mode(True, self)
            self.select_y_button.Enable()
        else:
            self.main_frame.enable_select_mode(False, self)

    
    def set_selection(self, selection_str):
        if self.__selecting_x:
            self.xseries_box.SetValue(selection_str)
        else:
            self.yseries_box.SetValue(selection_str)
        
        
class DataSeriesSelectPanel(wx.ScrolledWindow):
    def __init__(self, parent, main_frame, file_contents):
        wx.ScrolledWindow.__init__(self, parent, wx.ID_ANY)
        self.SetScrollRate(5,5)
        self.file_contents = file_contents
        box = wx.StaticBox(self, wx.ID_ANY, "Data Series")
        self.vsizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        self.main_frame = main_frame
        #TODO - these would be better implemented as an ordered dict
        self.data_series = []
        self.data_series_id_mapping = {} #{id:index in data_series}
        

        self.on_add_data_series(None)
        
        self.SetSizer(self.vsizer)
        self.vsizer.Fit(self)
        self.SetAutoLayout(True)
        
    
    def enable_select_mode(self, val, series):
        for s in self.data_series:
            s.enable_select_mode(val, series)
        
    def on_add_data_series(self, evnt):
        series = XYDataSeriesPanel(self, self.file_contents, self.main_frame) #remove button only if it is not the first series
        series.set_button_visibility(True, bool(self.data_series))
        self.vsizer.Add(series,1, wx.EXPAND | wx.ALIGN_TOP)
        if self.data_series:
            self.data_series[-1].set_button_visibility(False, True)
        self.data_series.append(series)
        self.data_series_id_mapping[series.get_remove_button_id()] = series
        wx.EVT_BUTTON(self, self.data_series[-1].get_add_button_id(), self.on_add_data_series)   
        wx.EVT_BUTTON(self, self.data_series[-1].get_remove_button_id(), self.on_remove_data_series)
        self.SendSizeEvent()
    
    
    def on_remove_data_series(self, evnt):
        
        id_ = evnt.Id
        series =  self.data_series_id_mapping[id_]
        self.data_series_id_mapping.pop(id_)
        idx = self.data_series.index(series)
        
        if idx == len(self.data_series) -1:
            self.data_series[-2].set_button_visibility(True, len(self.data_series)>2)       
        elif idx == 0:
            self.data_series[1].set_button_visibility(len(self.data_series)<3, len(self.data_series)>2)
        elif len(self.data_series)<3:
            self.data_series[0].set_button_visibility(True, False)
        
        self.data_series[idx].Destroy()
        self.data_series.remove(series)
        self.SendSizeEvent()
        
        
        
        
        
class TxtFileDataSeriesSelectFrame(wx.Dialog):
    def __init__(self, parent, file_contents):
        #set the title to the file name
        frame_title = "%s - Data Select - %s" %(file_contents.filename,avoplot.PROG_SHORT_NAME)     
        wx.Dialog.__init__(self, parent, wx.ID_ANY, frame_title, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.filename = file_contents.filename
        
        #set up the icon for the frame
        self.SetIcon(wx.ArtProvider.GetIcon("avoplot"))
        
        #create top level panel to hold all frame elements
        top_panel = wx.Panel(self, wx.ID_ANY)
        
        #create top level sizer to contain all frame elements
        topsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        topsizer.Add(vsizer, 1, wx.EXPAND)
        
        #create all the frame elements
        self.file_contents_panel = FileContentsPanel(top_panel, file_contents)
        self.data_series_panel = DataSeriesSelectPanel(top_panel, self, file_contents)
        vsizer.Add(self.file_contents_panel, 5, wx.EXPAND | wx.ALL, border=5)
        vsizer.Add(self.data_series_panel, 1, wx.EXPAND | wx.ALL, border=5)
            
        #create main buttons
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.plot_button = wx.Button(top_panel, wx.ID_ANY, "Plot")
        self.cancel_button = wx.Button(top_panel, wx.ID_ANY, "Cancel")
        buttons_sizer.Add(self.cancel_button, 1, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM)
        buttons_sizer.Add(self.plot_button, 1, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM) 
        wx.EVT_BUTTON(self, self.plot_button.GetId(), self.on_plot)
        wx.EVT_BUTTON(self, self.cancel_button.GetId(), self.on_cancel)

        vsizer.Add(buttons_sizer, 0, wx.ALL | wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT, border=10)
        
        #configure layout and position
        top_panel.SetSizer(topsizer)
        topsizer.Fit(top_panel)
        top_panel.SetAutoLayout(True)
        self.Center(wx.BOTH)
        self.Show()

    def on_plot(self, evnt):
        for series in self.data_series_panel.data_series:
            try:
                #TODO - read the row data status from the checkbox
                series.validate_selection(False)
            except InvalidSelectionError,e:
                wx.MessageBox(e.args[0], avoplot.PROG_SHORT_NAME, wx.ICON_ERROR)
                return
        
        self.EndModal(wx.ID_OK)
        
    
    def on_cancel(self, evnt):
        self.EndModal(wx.ID_CANCEL)
    
    
    def enable_select_mode(self, val, data_series):
        self.file_contents_panel.enable_select_mode(val, data_series)
        self.data_series_panel.enable_select_mode(val, data_series)


    def get_series(self):
        series = []
        for s in self.data_series_panel.data_series:
            data = s.get_series_data()
            if data:
                series.append(XYDataSeries(os.path.basename(self.filename),xdata=data[0], ydata=data[1]))
        return series
    

    
class ColumnSelectorFrame(wx.Frame):
    def __init__(self, parent, file_contents):
        
        wx.Frame.__init__(self, parent, wx.ID_ANY)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        #top_panel = wx.Panel(self, wx.ID_ANY)
        n_cols = len(file_contents.columns)
        n_rows = file_contents.columns[0].get_number_of_rows()
        
        
        data_select_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        data_select_sizer.Add(wx.StaticText(self, -1, "x data:"), 0, wx.ALIGN_LEFT)
        self.x_selection_box = wx.TextCtrl(self, -1)
        data_select_sizer.Add(self.x_selection_box, 0, wx.ALIGN_LEFT)
        x_selection_button = wx.ToggleButton(self, -1, "Select")
        wx.EVT_TOGGLEBUTTON(self, x_selection_button.GetId(), self.on_x_select)
        data_select_sizer.Add(x_selection_button, 0, wx.ALIGN_LEFT)
        
        data_select_sizer.Add(wx.StaticText(self, -1, "y data:"), 0, wx.ALIGN_LEFT)
        self.y_selection_box = wx.TextCtrl(self, -1)
        data_select_sizer.Add(self.y_selection_box, 0, wx.ALIGN_LEFT)
        y_selection_button = wx.ToggleButton(self, -1, "Select")
        wx.EVT_TOGGLEBUTTON(self, y_selection_button.GetId(), self.on_y_select)
        data_select_sizer.Add(y_selection_button, 0, wx.ALIGN_LEFT)
  
        vsizer.Add(data_select_sizer, 0, wx.ALIGN_TOP)
        
        #create cells
        self.grid = wx.grid.Grid(self, wx.ID_ANY)
        
        
        
        self.grid.CreateGrid(n_rows, n_cols)
        
        for c, col in enumerate(file_contents.columns):
            if col.title and not col.title.isspace():
                self.grid.SetColLabelValue(c, col.title)
            
            for r, data in enumerate(col.raw_data):
                self.grid.SetCellValue(r, c, data)
        
        self.grid.AutoSize()      

        
        self.plot_button = wx.Button(self, wx.ID_ANY, "Plot")
        
        wx.EVT_BUTTON(self, self.plot_button.GetId(), self.on_plot)
        
        vsizer.Add(self.grid, 1, wx.EXPAND)
        vsizer.Add(self.plot_button, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizer(vsizer)
        vsizer.Fit(self)
        self.SetAutoLayout(True)
        self.Show()
        
    
    def on_x_select(self, evnt):
        if evnt.IsChecked():
            self.grid.EnableDragGridSize(False)  
            self.grid.EnableDragColSize(False)
            self.grid.EnableDragRowSize(False)
            self.grid.EnableEditing(False)
            wx.grid.EVT_GRID_RANGE_SELECT(self, self.on_x_range_selected)
            self.grid.GetGridWindow().SetCursor(wx.StockCursor(wx.CURSOR_CROSS))
        
        else:
            self.grid.EnableDragGridSize(True)  
            self.grid.EnableDragColSize(True)
            self.grid.EnableDragRowSize(True)
            self.grid.EnableEditing(True)
            wx.grid.EVT_GRID_RANGE_SELECT(self, None)
            self.grid.GetGridWindow().SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
    
    
    def on_y_select(self, evnt):
        if evnt.IsChecked():
            self.grid.EnableDragGridSize(False)  
            self.grid.EnableDragColSize(False)
            self.grid.EnableDragRowSize(False)
            self.grid.EnableEditing(False)
            wx.grid.EVT_GRID_RANGE_SELECT(self, self.on_y_range_selected)
            self.grid.GetGridWindow().SetCursor(wx.StockCursor(wx.CURSOR_CROSS))
        
        else:
            self.grid.EnableDragGridSize(True)  
            self.grid.EnableDragColSize(True)
            self.grid.EnableDragRowSize(True)
            self.grid.EnableEditing(True)
            wx.grid.EVT_GRID_RANGE_SELECT(self, None)
            self.grid.GetGridWindow().SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
        
                    
    def on_x_range_selected(self, evnt):
        if not evnt.Selecting():
            return 
        selection = (evnt.GetTopLeftCoords(), evnt.GetBottomRightCoords())
        self.x_selection_box.SetValue(str(selection))
        
        
    def on_y_range_selected(self, evnt):
        if not evnt.Selecting():
            return 
        selection = (evnt.GetTopLeftCoords(), evnt.GetBottomRightCoords())
        self.y_selection_box.SetValue(str(selection))        
        
        
    def on_plot(self, evnt):
        cols = self.grid.GetSelectedCols()
        print cols
