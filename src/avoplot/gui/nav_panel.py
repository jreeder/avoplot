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
from wx.lib.agw import customtreectrl
import warnings
from avoplot import core
from avoplot import series

class RightClickMenu(wx.Menu):
    """
    Popup menu displayed when elements in the navigation panel are
    right clicked.
    """
    def __init__(self, nav_panel):
        
        wx.Menu.__init__(self)
        
        rename_entry = self.Append(-1, 'Rename', 'Rename the element')
        wx.EVT_MENU(nav_panel,rename_entry.GetId(), nav_panel.on_rclick_menu_rename)
        
        delete_entry = self.Append(-1, 'Delete', 'Delete the element')
        wx.EVT_MENU(nav_panel,delete_entry.GetId(), nav_panel.on_rclick_menu_delete)
        
        self.export_entry = self.Append(-1, 'Export data', 'Export series to a text file')
        wx.EVT_MENU(nav_panel,self.export_entry.GetId(), nav_panel.on_rclick_menu_export)



class NavigationPanel(wx.ScrolledWindow):
    """
    Navigation panel for selecting plot elements in a tree ctrl.
    """
    def __init__(self, parent, session):
        super(NavigationPanel, self).__init__(parent)
        
        #enable the scroll bars on the scrolled window
        self.SetScrollRate(2, 2)
        
        self._rclick_menu = RightClickMenu(self)
        
        self.v_sizer = wx.BoxSizer(wx.VERTICAL)
        
        #note that we need a try except block for agwStyle because it 
        #changed names between wx versions from style to agwstyle
        try:
            self.tree = customtreectrl.CustomTreeCtrl(self, wx.ID_ANY, 
                                                      agwStyle=(customtreectrl.TR_HIDE_ROOT |
                                                                customtreectrl.TR_HAS_BUTTONS))
        except:
            self.tree = customtreectrl.CustomTreeCtrl(self, wx.ID_ANY, 
                                                      style=(customtreectrl.TR_HIDE_ROOT |
                                                                customtreectrl.TR_HAS_BUTTONS))
       
        #disable the scroll bars which come with the tree control (otherwise
        #you end up with two sets sometimes!)
        self.tree.EnableScrolling(False, False)
        self.SetScrollbars(0,0,0,0)
        
        self.v_sizer.Add(self.tree,1,wx.EXPAND)
        self.__current_selection_id = None
        
        #add the session element as the root node
        root = self.tree.AddRoot(session.get_name(), 
                                 data=wx.TreeItemData(session))
        self.__el_id_mapping = {session.get_avoplot_id():root}
        
        #bind avoplot events
        core.EVT_AVOPLOT_ELEM_SELECT(self, self.on_element_select)
        core.EVT_AVOPLOT_ELEM_DELETE(self, self.on_element_delete)
        core.EVT_AVOPLOT_ELEM_ADD(self, self.on_element_add)
        core.EVT_AVOPLOT_ELEM_RENAME(self, self.on_element_rename)
        
        #bind wx events
        wx.EVT_TREE_SEL_CHANGED(self, self.tree.GetId(), self.on_tree_select_el)
        wx.EVT_TREE_ITEM_MENU(self, self.tree.GetId(), self.on_tree_el_menu)
        
        #do the layout 
        self.SetSizer(self.v_sizer)
        self.v_sizer.Fit(self)
        self.SetAutoLayout(True)
 
 
    def on_rclick_menu_delete(self, evnt):
        """
        Event handler for the delete option in the right click menu.
        """
        el_id = self.__el_id_mapping[self.__current_selection_id]
        el = self.tree.GetPyData(el_id).GetData()
        el.delete()   
    
    
    def on_rclick_menu_rename(self, evnt):
        """
        Event handler for the rename option in the right click menu.
        
        Opens a dialog box for the user to enter the new element name.
        """
        el_id = self.__el_id_mapping[self.__current_selection_id]
        el = self.tree.GetPyData(el_id).GetData()
        
        current_name = el.get_name()
        
        #pass dialog None as parent so that it gets centred within 
        #the top window
        d = wx.TextEntryDialog(None, "New name:", "Rename", 
                               defaultValue=current_name)
        
        if d.ShowModal() == wx.ID_OK:
            new_name = d.GetValue()
            if (new_name and not new_name.isspace() and 
                new_name != current_name):
                el.set_name(str(new_name))
                
                
    def on_rclick_menu_export(self, evnt):
        """
        Event handler for the export option in the right click menu.
        """
        el_id = self.__el_id_mapping[self.__current_selection_id]
        el = self.tree.GetPyData(el_id).GetData()
        el.export()
    
    
    def on_tree_el_menu(self, evnt):
        """
        Event handler for right click events on elements in the navigation 
        panel - opens a popup menu for the element clicked.
        """
        el_id = self.__el_id_mapping[self.__current_selection_id]
        el = self.tree.GetPyData(el_id).GetData()
        
        if not hasattr(el, 'export'):
            if self._rclick_menu.export_entry in self._rclick_menu.GetMenuItems():
                self._rclick_menu.RemoveItem(self._rclick_menu.export_entry)
            self.PopupMenu(self._rclick_menu)
        else:
            if self._rclick_menu.export_entry not in self._rclick_menu.GetMenuItems(): 
                self._rclick_menu.InsertItem(self._rclick_menu.GetMenuItemCount(),
                                              self._rclick_menu.export_entry)
            self.PopupMenu(self._rclick_menu)
        
    
    def on_tree_select_el(self, evnt):
        """
        Event handler for tree item select. Selects the corresponding AvoPlot
        element (which generates an AvoPlotElementSelect) 
        """
        #get the avoplot element and set it selected
        tree_node_id = evnt.GetItem()
        el = self.tree.GetPyData(tree_node_id).GetData()
        self.__current_selection_id = el.get_avoplot_id()
        el.set_selected()
    
        
    def on_element_select(self, evnt):
        """
        Event handler for AvoPlotElementSelect events. Selects the tree item 
        corresponding to the element which has been selected.
        """
        el = evnt.element
        
        #if the element is our current selection, then do nothing
        if el.get_avoplot_id() == self.__current_selection_id:
            return
        
        #if the element exists in the tree then select it
        if self.__el_id_mapping.has_key(el.get_avoplot_id()):
            self.tree.SelectItem(self.__el_id_mapping[el.get_avoplot_id()])
            self.__current_selection_id = el.get_avoplot_id()
            return 
        
        else:
            warnings.warn("element not in tree"+str(el))

               
    def on_element_delete(self, evnt):
        """
        Event handler for AvoPlotElementDelete events. Removes the tree item 
        corresponding to the element which has been deleted.
        """
        el = evnt.element
        if self.__el_id_mapping.has_key(el.get_avoplot_id()):
            tree_item = self.__el_id_mapping.pop(el.get_avoplot_id())
            self.tree.Delete(tree_item)
    
        
    def on_element_add(self, evnt):
        """
        Event handler for AvoPlotElementAdd events. Adds a tree item 
        for the element which has been added and all its children (recursively).
        """
        el = evnt.element

        parent_id = el.get_parent_element().get_avoplot_id()
        if self.__el_id_mapping.has_key(parent_id):
            parent_node = self.__el_id_mapping[parent_id]
            
            #add the elements children to the tree recursively
            self._add_all_child_nodes(parent_node, el)
            
            self.tree.ExpandAllChildren(parent_node)

        
    def on_element_rename(self, evnt):
        """
        Event handler for AvoPlotElementRename events. Renames the tree item 
        for the element which has been renamed.       
        """
        el = evnt.element
        if self.__el_id_mapping.has_key(el.get_avoplot_id()):
            tree_node = self.__el_id_mapping[el.get_avoplot_id()]
            self.tree.SetItemText(tree_node, el.get_name())
        
            
    def _add_all_child_nodes(self, parent_node, element):
        """
        Creates tree items recursively for all child elements below element, and 
        also adds a tree item for element to parent_node.
        """
        if not self.__el_id_mapping.has_key(element.get_avoplot_id()):
            node = self.tree.AppendItem(parent_node, element.get_name(), 
                                        data=wx.TreeItemData(element))
            self.__el_id_mapping[element.get_avoplot_id()] = node
        else:
            node = self.__el_id_mapping[element.get_avoplot_id()]
        
        for c in element.get_child_elements():
            self._add_all_child_nodes(node, c)
