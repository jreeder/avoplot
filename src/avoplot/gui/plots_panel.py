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
from wx import aui

from avoplot import figure
from avoplot import core
from avoplot.gui import menu


class PlotsPanel(aui.AuiNotebook):
    def __init__(self, parent):
        aui.AuiNotebook.__init__(self, parent, id=wx.ID_ANY, 
                                 style=aui.AUI_NB_DEFAULT_STYLE)
        
        self._tab_menu = menu.TabRightClickMenu(self)
        
        #register avoplot event handlers
        core.EVT_AVOPLOT_ELEM_SELECT(self, self.on_select_element)
        core.EVT_AVOPLOT_ELEM_ADD(self, self.on_new_element)
        core.EVT_AVOPLOT_ELEM_DELETE(self, self.on_delete_element)
        core.EVT_AVOPLOT_ELEM_RENAME(self, self.on_rename_element)        
        
        #register wx event handlers
        aui.EVT_AUINOTEBOOK_PAGE_CLOSE(self, self.GetId(), 
                                       self.on_tab_close)
        aui.EVT_AUINOTEBOOK_PAGE_CHANGED(self, self.GetId(), 
                                         self.on_tab_change)
        
        try:
            aui.EVT_AUINOTEBOOK_TAB_RIGHT_DOWN(self, self.GetId(), 
                                               self.on_tab_right_click)
        except AttributeError:
            #new version of wx has renamed this for some reason!
            aui.EVT__AUINOTEBOOK_TAB_RIGHT_DOWN(self, self.GetId(), 
                                                self.on_tab_right_click)
    
    
    def on_tab_change(self, evnt):
        print "on tab change"
        idx = self.GetSelection()
        fig = self.GetPage(idx)
        fig.set_selected()
    
    
    def on_tab_close(self, evnt):
        print "on tab close"
        #don't let the notebook actually close the tab, otherwise it will 
        #destroy the window as well
        evnt.Veto() 
        
        idx = self.GetSelection()
        fig = self.GetPage(idx)
        
        #rely on the AVOPLOT_ON_ELEM_DELETE event to destroy the window
        fig.delete() 
        
    
    def on_new_element(self, evnt):
        el = evnt.element
        if isinstance(el, figure.AvoPlotFigure):
            self.AddPage(el, el.get_name())
    
    
    def on_select_element(self, evnt):
        el = evnt.element
        while not isinstance(el, figure.AvoPlotFigure):
            el = el.get_parent_element()
            if el is None:
                #this should never happen - but just in case
                return

        idx = self.GetPageIndex(el)
        if idx >= 0:
            if idx != self.GetSelection():
                try:
                    self.ChangeSelection(idx) #only available in wx >V2.9.3
                except AttributeError:
                    self.SetSelection(idx)
                    
    
    
    def on_delete_element(self, evnt):
        print "plots panel on delete",evnt.element.get_name()
        #return
        el = evnt.element
        
        if isinstance(el, figure.AvoPlotFigure):
            idx = self.GetPageIndex(el)
            if idx >= 0:
                self.DeletePage(idx)
            
    def on_rename_element(self, evnt):
        el = evnt.element
        if isinstance(el, figure.AvoPlotFigure):
            idx = self.GetPageIndex(el)
            if idx >= 0:
                self.SetPageText(idx, el.get_name())
            
    
    def on_tab_right_click(self, evnt):
        idx = evnt.GetSelection()
        fig = self.GetPage(idx)
        fig.set_selected()
        self.PopupMenu(self._tab_menu)
    
    
    def rename_current_figure(self, evnt):
        idx = self.GetSelection()
        fig = self.GetPage(idx)
        current_name = fig.get_name()
        
        d = wx.TextEntryDialog(self, "Plot name:", "Rename", 
                               defaultValue=current_name)
        
        if d.ShowModal() == wx.ID_OK:
            new_name = d.GetValue()
            if (new_name and not new_name.isspace() and 
                new_name != current_name):
                fig.set_name(str(new_name))


    def split_figure_horiz(self, *args):
        self.Split(self.GetSelection(), wx.RIGHT)
       
        
    def split_figure_vert(self, *args):
        self.Split(self.GetSelection(), wx.BOTTOM)    
        
        
    def unsplit_panes(self, *args):
        self.Freeze()

        # remember the tab now selected
        nowSelected = self.GetSelection()
        # select first tab as destination
        self.SetSelection(0)
        # iterate all other tabs
        for idx in xrange(1, self.GetPageCount()):
            # get win reference
            win = self.GetPage(idx)
            # get tab title
            title = self.GetPageText(idx)
            # get page bitmap
            bmp = self.GetPageBitmap(idx)
            # remove from notebook
            self.RemovePage(idx)
            # re-add in the same position so it will tab
            self.InsertPage(idx, win, title, False, bmp)
        # restore orignial selected tab
        self.SetSelection(nowSelected)

        self.Thaw()
       
        #self.notebook.UnSplit()
        
        