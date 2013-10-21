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

from avoplot.subplots import AvoPlotSubplotBase, AvoPlotXYSubplot
from avoplot import controls
from avoplot import core
from avoplot import subplots
from avoplot import figure
from avoplot.gui import widgets
from avoplot.persist import PersistentStorage


class DataSeriesBase(core.AvoPlotElementBase):
    """
    Base class for all data series.
    """
    
    def __init__(self, name):
        super(DataSeriesBase, self).__init__(name)
        self.__plotted = False
        self._mpl_lines = []
        
        
#    def set_parent_element(self, parent):
#        """
#        Overrides AvoPlotElementBase method. Does exactly the same, but ensures 
#        that parent is an instance of AvoPlotSubplotBase or a subclass thereof.
#        """
#        assert isinstance(parent, AvoPlotSubplotBase) or parent is None
#        super(DataSeriesBase, self).set_parent_element(parent)
    
    
    def get_mpl_lines(self):
        """
        Returns a list of matplotlib line objects associated with the data 
        series.
        """
        assert self.__plotted, ('Data series must be plotted before you can '
                                'access the matplotlib lines')
        return self._mpl_lines
    
    
    def get_figure(self):
        """
        Returns the AvoPlot figure (avoplot.figure.AvoPlotFigure) object that
        the series is contained within, or None if the series does not yet 
        belong to a figure.
        """
        #look up the list of parents recursively until we find a figure object
        parent = self.get_parent_element()
        while not isinstance(parent, figure.AvoPlotFigure):
            if parent is None:
                return None
            parent = parent.get_parent_element()
            
            #sanity check - there should always be a figure object somewhere
            #in the ancestry of a series object.
            if isinstance(parent, core.AvoPlotSession):
                raise RuntimeError("Reached the root element before an "
                                   "AvoPlotFigure instance was found.")
        return parent
    
    
    def get_subplot(self):
        """
        Returns the AvoPlot subplot (subclass of 
        avoplot.subplots.AvoPlotSubplotBase) object that
        the series is contained within, or None if the series does not yet 
        belong to a subplot.
        """
        #look up the list of parents recursively until we find a figure object
        parent = self.get_parent_element()
        while not isinstance(parent, subplots.AvoPlotSubplotBase):
            if parent is None:
                return None
            parent = parent.get_parent_element()
            
            #sanity check - there should always be a figure object somewhere
            #in the ancestry of a series object.
            if isinstance(parent, core.AvoPlotSession):
                raise RuntimeError("Reached the root element before an "
                                   "AvoPlotFigure instance was found.")
        return parent
        
    
    def delete(self):
        """
        Overrides the base class method in order to remove the line(s) from the 
        axes and draw the changes. 
        """
        self._mpl_lines.pop(0).remove()
        self.update()
        super(DataSeriesBase, self).delete()        
        
        
    def _plot(self, subplot):
        """
        Called in subplot.add_data_series() to plot the data into the subplot
        and setup the controls for the series (the parent of the series is not
        known until it gets added to the subplot)
        """
        #assert isinstance(subplot, AvoPlotSubplotBase), ('arg passed as '
        #        'subplot is not an AvoPlotSubplotBase instance')
        
        assert not self.__plotted, ('plot() should only be called once')
        
        self.__plotted = True
        
        self._mpl_lines = self.plot(subplot)
        self.setup_controls(subplot.get_figure())
    
    
    def add_subseries(self, series):
        """
        """
        series.set_parent_element(self)
        series._plot(self.get_subplot())
    
    
    def update(self):
        """
        Redraws the series.
        """
        subplot = self.get_subplot()
        if subplot: #subplot could be None - in which case do nothing
            subplot.update()
    
    
    def plot(self, subplot):
        """
        Plots the data series into the specified subplot (AvoPlotSubplotBase 
        instance) and returns the list of matplotlib lines associated with the 
        series. This method should be overridden by subclasses.
        """
        return []
    
    
    def preprocess(self, *args):
        """
        Runs any preprocessing required on the data and returns it. This 
        should be overridden by subclasses.
        """
        #return the data passed in unchanged
        return args
    
    
    def is_plotted(self):
        """
        Returns True if the series has already been plotted. False otherwise.
        """
        return self.__plotted   



class XYDataSeries(DataSeriesBase):
    """
    Class to represent 2D XY data series.
    """
    def __init__(self, name, xdata=None, ydata=None):
        super(XYDataSeries, self).__init__(name)
        self.set_xy_data(xdata, ydata)
        self.add_control_panel(XYSeriesControls(self))
        
          
    @staticmethod    
    def get_supported_subplot_type():
        """
        Static method that returns the class of subplot that the data series
        can be plotted into. This will be a subclass of AvoPlotSubplotBase.
        """
        return AvoPlotXYSubplot
    
    
    def set_xy_data(self, xdata=None, ydata=None):
        """
        Sets the x and y values of the data series. Note that you need to call
        the update() method to draw the changes to the screen.
        """
        if xdata is None and ydata is None:
            xdata = []
            ydata = []
            
        elif xdata is None:
            xdata = range(len(ydata))
            
        elif ydata is None:
            ydata = range(len(xdata))
            
        else:
            assert len(xdata) == len(ydata)
        
        self.__xdata = xdata
        self.__ydata = ydata
        
        if self.is_plotted():
            #update the the data in the plotted line
            line, = self.get_mpl_lines()
            line.set_data(*self.preprocess(self.__xdata, self.__ydata))
    
    
    def get_raw_data(self):
        """
        Returns a tuple (xdata, ydata) of the raw data held by the series 
        (without any pre-processing operations performed). In general you should
        use the get_data() method instead.
        """
        return (self.__xdata, self.__ydata)
    
    
    def get_data(self):
        """
        Returns a tuple (xdata, ydata) of the data held by the series, with
        any pre-processing operations applied to it.
        """
        return self.preprocess(numpy.array(self.__xdata), numpy.array(self.__ydata))
    
    
    def preprocess(self, xdata, ydata):
        """
        Runs any required preprocessing operations on the x and y data and
        returns them.
        """
        xdata, ydata = super(XYDataSeries, self).preprocess(xdata, ydata)
        return xdata, ydata
        
    
    def plot(self, subplot):
        """
        plots the x,y data into the subplot as a line plot.
        """
        return subplot.get_mpl_axes().plot(*self.get_data())
    
    
    def export(self):
        """
        Exports the selected data series. Called when user right clicks on the data series (see nav_panel.py).
        """
        persistant_storage = PersistentStorage()
        
        try:
            last_path_used = persistant_storage.get_value("series_export_last_dir_used")
        except KeyError:
            last_path_used = ""
            
        export_dialog = wx.FileDialog(None, message="Export data series as...",
                                       defaultDir=last_path_used, defaultFile="AvoPlot Series.txt",
                                       style=wx.SAVE|wx.FD_OVERWRITE_PROMPT, wildcard = "TXT files (*.txt)|*.txt")
        
        if export_dialog.ShowModal() == wx.ID_OK:
            path = export_dialog.GetPath()
            persistant_storage.set_value("series_export_last_dir_used", os.path.dirname(path))
            xdata, ydata = self.get_data()
            
            with open(path, 'w') as fp:
                for i in range(len(xdata)):
                    if isinstance(xdata[0], datetime):
                        fp.write("%s\t%f\n" %(str(xdata[i]), ydata[i]))
                        #yfloat = []
                        #for i in ydata:
                        #    yfloat.append(time.mktime(ydata[i].timetuple()))
                        #fp.write("%f\t%f\n" %(xdata[i], yfloat[i]))
                    else:
                        fp.write("%f\t%f\n" %(xdata[i], ydata[i]))

        
        export_dialog.Destroy()            


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




class XYSeriesControls(controls.AvoPlotControlPanelBase):
    """
    Control panel to allow user editing of data series (line styles,
    colours etc.)
    """
    
    def __init__(self, series):
        super(XYSeriesControls, self).__init__("Series")
        self.series = series
        
               
    def setup(self, parent):
        """
        Creates all the controls in the panel
        """
        super(XYSeriesControls, self).setup(parent)
        mpl_lines = self.series.get_mpl_lines()
        
        #explicitly set the the marker colour to its existing value, otherwise
        #it will get changed if we change the line colour
        mpl_lines[0].set_markeredgecolor(mpl_lines[0].get_markeredgecolor())
        mpl_lines[0].set_markerfacecolor(mpl_lines[0].get_markerfacecolor())
        
        #add line controls
        line_ctrls_static_szr = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, 'Line'), wx.VERTICAL)
        
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
        
        
        #add the marker controls
        marker_ctrls_static_szr = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, 'Markers'), wx.VERTICAL)
        
        marker_ctrls_szr = wx.FlexGridSizer(5, 2, vgap=5, hgap=2)
        
        #marker style
        self.marker_style_choice = wx.Choice(self, wx.ID_ANY, 
                                             choices=[m.name for m in available_markers])        
        
        marker_ctrls_szr.Add(wx.StaticText(self, wx.ID_ANY, "Style:"), 0,
                             wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT)
        marker_ctrls_szr.Add(self.marker_style_choice, 0,
                             wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT)
        wx.EVT_CHOICE(self, self.marker_style_choice.GetId(), self.on_marker)
        
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

        
        line_ctrls_static_szr.Add(line_ctrls_szr, 0, wx.ALIGN_RIGHT)
        
        marker_ctrls_static_szr.Add(marker_ctrls_szr, 0, wx.ALIGN_RIGHT)
        self.Add(line_ctrls_static_szr, 0, wx.ALIGN_LEFT | wx.EXPAND | wx.ALL, border=5)
        self.Add(marker_ctrls_static_szr, 0, wx.ALIGN_LEFT | wx.EXPAND | wx.ALL, border=5)
        
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
        
        
        #set the marker selection to that of the data
        #it is possible that the marker will have been set to something that
        #avoplot does not yet support - if so, default to None and issue warning
        if marker_symbol_to_idx_map.has_key(mpl_lines[0].get_marker()):
            #everything is fine
            current_marker_idx = marker_symbol_to_idx_map[mpl_lines[0].get_marker()]
        else:
            current_marker_idx = 0
            warnings.warn("Data series has an unsupported marker style. "
                          "Defaulting to a marker style of \'None\' instead.")
        
        #update the GUI appropriately for the current marker selection
        self.marker_style_choice.SetSelection(current_marker_idx)
        self.update_marker_controls(available_markers[current_marker_idx])
        

    
    
    def on_marker_fillcolour(self, evnt):
        """
        Event handler for marker fill colour change events
        """
        l, = self.series.get_mpl_lines()
        l.set_markerfacecolor(evnt.GetColour().GetAsString(wx.C2S_HTML_SYNTAX))
        self.series.update()
    
    
    def on_marker_edgecolour(self, evnt):
        """
        Event handler for marker fill colour change events
        """
        l, = self.series.get_mpl_lines()
        l.set_markeredgecolor(evnt.GetColour().GetAsString(wx.C2S_HTML_SYNTAX))
        self.series.update()
        
        
    def on_marker_edgewidth(self, evnt):
        """
        Event handler for line thickness change events.
        """
        l, = self.series.get_mpl_lines()
        l.set_markeredgewidth(self.marker_edgewidth_ctrl.GetValue())
        self.series.update()
            
            
    def on_marker(self, evnt):
        """
        Event handler for marker style change events.
        """
        marker_idx = marker_name_to_idx_map[evnt.GetString()]
        new_marker = available_markers[marker_idx]
        self.update_marker_controls(new_marker)
        l, = self.series.get_mpl_lines()
        l.set_marker(new_marker.mpl_symbol)
        self.series.update()
    
    
    def on_markersize(self, evnt):
        """
        Event handler for marker size change events
        """
        l, = self.series.get_mpl_lines()
        l.set_markersize(self.marker_size_ctrl.GetValue())
        self.series.update()
    
    
    def on_line_colour_change(self, evnt):
        """
        Event handler for line colour change events.
        """
        l, = self.series.get_mpl_lines()
        l.set_color(evnt.GetColour().GetAsString(wx.C2S_HTML_SYNTAX))
        self.series.update()
        
    
    def on_linestyle(self, evnt):
        """
        Event handler for line style change events.
        """
        line_idx = line_name_to_idx_map[evnt.GetString()]
        new_line = available_lines[line_idx]
        self.update_line_controls(new_line)
        l, = self.series.get_mpl_lines()
        l.set_linestyle(new_line.mpl_symbol)
        self.series.update()
        
        
    
    def on_linewidth(self, evnt):
        """
        Event handler for line thickness change events.
        """
        l, = self.series.get_mpl_lines()
        l.set_linewidth(self.line_weight_ctrl.GetValue())
        self.series.update()
                
    
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
        
        
            
