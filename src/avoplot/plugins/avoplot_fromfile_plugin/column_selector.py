from avoplot.gui.artwork import AvoplotArtProvider
import wx
import wx.lib.agw
import wx.grid



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
            header_pane = wx.CollapsiblePane(self, wx.ID_ANY, "File Header")
            win = header_pane.GetPane()
            header_txt_ctrl = wx.TextCtrl(win, wx.ID_ANY, value=file_contents.header,
                                          style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
            
            header_pane_sizer = wx.BoxSizer(wx.VERTICAL)
            header_pane_sizer.Add(header_txt_ctrl, 1, wx.GROW | wx.ALL, border=5)
            
            win.SetSizer(header_pane_sizer)
            header_pane_sizer.SetSizeHints(win)
            wx.EVT_COLLAPSIBLEPANE_CHANGED(self, header_pane.GetId(), self.on_expand)
            
            vsizer.Add(header_pane, 0, wx.GROW)
        
        
        #add the grid panel for data selection
        grid_panel = ColumnDataPanel(self, file_contents)
        vsizer.Add(grid_panel, 1, wx.EXPAND)

        #add a drop-down panel for displaying the file footer contents (if there is any)
        if file_contents.footer:
            footer_pane = wx.CollapsiblePane(self, wx.ID_ANY, "File Footer")
            win = footer_pane.GetPane()
            footer_txt_ctrl = wx.TextCtrl(win, wx.ID_ANY, value=file_contents.footer,
                                          style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
            
            footer_pane_sizer = wx.BoxSizer(wx.VERTICAL)
            footer_pane_sizer.Add(footer_txt_ctrl, 1, wx.GROW | wx.ALL, border=5)
            
            win.SetSizer(footer_pane_sizer)
            footer_pane_sizer.SetSizeHints(win)
            wx.EVT_COLLAPSIBLEPANE_CHANGED(self, footer_pane.GetId(), self.on_expand)
            
            vsizer.Add(footer_pane, 0, wx.GROW)
        
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



class ColumnDataPanel(wx.Panel):
    def __init__(self, parent, file_contents):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        
        n_cols = len(file_contents.columns)
        n_rows = file_contents.columns[0].get_number_of_rows()
        
        vsizer = wx.BoxSizer(wx.VERTICAL)
        
        #create cells
        self.grid = wx.grid.Grid(self, wx.ID_ANY)

        self.grid.CreateGrid(n_rows, n_cols)
        vsizer.Add(self.grid, 1, wx.EXPAND)
        
        for c, col in enumerate(file_contents.columns):
            if col.title and not col.title.isspace():
                self.grid.SetColLabelValue(c, col.title)
            
            for r, data in enumerate(col.raw_data):
                self.grid.SetCellValue(r, c, data)
        
        self.grid.AutoSize() 
        self.SetSizer(vsizer)
        vsizer.Fit(self)
   
   
    def set_editable(self, value):
        self.grid.EnableDragGridSize(value)  
        self.grid.EnableDragColSize(value)
        self.grid.EnableDragRowSize(value)
        self.grid.EnableEditing(value)
            
   
   
        
class DataSeriesPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        box = wx.StaticBox(self, wx.ID_ANY, "Data Series")
        vsizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        
        #box = wx.StaticBox(self, wx.ID_ANY, "File Contents")
        #vsizer.Add(box,1,wx.EXPAND)
        vsizer.Add(wx.StaticText(self, -1, "test text"), 1)
        
        self.SetSizer(vsizer)
        vsizer.Fit(self)
        self.SetAutoLayout(True)       
        
        
class TxtFileDataSeriesSelectFrame(wx.Frame):
    def __init__(self, parent, file_contents):
        #set the title to the file name
        frame_title = "%s - Data Select - AvoPlot" % file_contents.filename        
        wx.Frame.__init__(self, parent, wx.ID_ANY, frame_title)
        
        #set up the icon for the frame
        self.art_provider = AvoplotArtProvider()
        wx.ArtProvider.Push(self.art_provider)
        self.SetIcon(self.art_provider.GetIcon("AvoPlot"))
        
        #create top level panel to hold all frame elements
        top_panel = wx.Panel(self, wx.ID_ANY)
        
        #create top level sizer to contain all frame elements
        topsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        topsizer.Add(vsizer, 1, wx.EXPAND)
        
        #create all the frame elements
        self.file_contents_panel = FileContentsPanel(top_panel, file_contents)
        self.data_series_panel = DataSeriesPanel(top_panel)
        vsizer.Add(self.file_contents_panel, 2, wx.EXPAND | wx.ALL, border=5)
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
        top_panel.SetSizer(vsizer)
        topsizer.Fit(self)
        top_panel.SetAutoLayout(True)
        self.Center(wx.BOTH)
        self.Show()

    def on_plot(self, evnt):
        pass
    
    def on_cancel(self, evnt):
        self.Destroy()




    
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
