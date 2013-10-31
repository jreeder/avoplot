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
Unit tests for the avoplot.core module
"""

import unittest
from avoplot import core

class ElementParentingTestCase(unittest.TestCase):
    def setUp(self):
        self.parent_el = core.AvoPlotElementBase('parent')
        self.child_el = core.AvoPlotElementBase('child')
        
        
    def test_add_remove_child_element(self):
        
        #test adding a child element to a parent
        self.child_el.set_parent_element(self.parent_el)
        self.assertEqual(len(self.parent_el.get_child_elements()), 1)
        self.assertEqual(self.parent_el.get_child_elements()[0], self.child_el)
        self.assertEqual(self.child_el.get_parent_element(), self.parent_el)
        
        #test removing the child again
        self.child_el.set_parent_element(None)
        self.assertEqual(self.parent_el.get_child_elements(), [])
        self.assertIsNone(self.child_el.get_parent_element())

if __name__ == '__main__':
    unittest.main()
        
        
         