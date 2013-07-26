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

import warnings
import mimetypes
import wx
import re
import StringIO
import os.path
from avoplot.plugins import AvoPlotPluginSimple
from avoplot.series import XYDataSeries
from avoplot.persist import PersistentStorage
from column_selector import TxtFileDataSeriesSelectFrame
#from avoplot.plugins.avoplot_fromfile_plugin.loader import FileLoaderBase
import loader


try:
    import magic
    have_magic = True
    
    try:
        magic.Magic()
    except Exception, e:
        warnings.warn(("Your python-magic installation seems to be broken. "
                      "Error message was \'%s\'. Using mimetypes module instead."%e.args))
        have_magic = False
        
except ImportError:
    have_magic = False


#required otherwise plugin will not be loaded!
plugin_is_GPL_compatible = True


def tuple_compare(first, second, element=0):
    """
    Compares two tuples based on their values at the index given by element.
    Use functools.partial() to build comparators for any element value for use
    in sort() functions.
    >>> print tuple_compare((1,2),(1,2))
    0
    >>> print tuple_compare((1,2),(2,1))
    -1
    >>> print tuple_compare((1,2),(2,1),element=1)
    1
    """
    return cmp(first[element], second[element])


def multi_sort(*lists):
    """
    Sorts multiple lists based on the contents of the first list.
    >>> print multi_sort([3,2,1],['a','b','c'],['d','e','f'])
    ([1, 2, 3], ['c', 'b', 'a'], ['f', 'e', 'd'])
    >>> print multi_sort([3,2,1])
    ([1, 2, 3],)
    """
    l = zip(*lists)
    l.sort(cmp=tuple_compare)
    return tuple([list(t) for t in zip(*l)])


def load(filename):
    with open(filename,'rb') as ifp:
        s = ifp.read()
    return StringIO.StringIO(s)

class TextFilePlugin(AvoPlotPluginSimple):
    def __init__(self):
        AvoPlotPluginSimple.__init__(self,"Text File", XYDataSeries)
        self.set_menu_entry(['From file'], "Plot data from a file")
    
    
    def plot_into_subplot(self, subplot):
        
        data_series = self.get_data_series()
        
        if not data_series:
            return False
        
        for s in data_series:
            subplot.add_data_series(s)
        
        return True
    
    
    def get_data_series(self):
        persistant_storage = PersistentStorage()
        
        try:
            last_path_used = persistant_storage.get_value("fromfile_last_dir_used")
        except KeyError:
            last_path_used = ""
        
        #get filename to open
        file_to_open = wx.FileSelector("Choose file to open", default_path=last_path_used)
        if file_to_open == "":
            return
        
        persistant_storage.set_value("fromfile_last_dir_used", os.path.dirname(file_to_open))
        
        wx.BeginBusyCursor()
        try:
            contents = loader.load_file(file_to_open)
            series_select_dialog = TxtFileDataSeriesSelectFrame(self.get_parent(), contents)
        finally:
            wx.EndBusyCursor()
        
        if series_select_dialog.ShowModal() == wx.ID_OK:
            return series_select_dialog.get_series()
            

def is_binary(ifp):
    """Return true if the given filename is binary. This is done
    based on finding null bytes in the file - it will only be used
    when python-magic is not available.
    """
    while 1:
        chunk = ifp.read(2048)
        if '\0' in chunk: # found null byte
            return True
        if len(chunk) < 2048:
            break # done
    return False
        
        
class TextFileLoader(loader.FileLoaderBase):
    
    def __init__(self):
        self.name = "Text file loader"
        
        
    def test(self, filename, ifp):
        
        if have_magic:
            try:
                file_type = magic.from_buffer(ifp.read(),mime=True)
            except Exception, e:
                print e.args
                return False
            finally:
                ifp.seek(0)
            
            if file_type.startswith('text/'):
                return True
            else:
                return False
        else:
            try:
                file_type = mimetypes.guess_type(filename)[0]
                if file_type and file_type.startswith('text/'):
                    return True
                else:
                    if is_binary(ifp):
                        return False
                    return True
            except Exception, e:
                print e.args
                return False
            
    
    
    def load(self, filename,ifp):
        comment = self.guess_comment_symbol(ifp)
        n_cols = self.guess_number_of_columns(ifp)
        start_idx, end_idx, lines_to_skip = self.guess_data_lines(ifp, n_cols, comment)
        headings = self.guess_column_titles(ifp, n_cols, start_idx, comment)
        header,columns,footer = self.get_columns(ifp, n_cols, start_idx, end_idx, lines_to_skip, headings)
        
        return loader.FileContents(filename, columns, header=header, comment_symbols=[comment], skipped_rows=[(i,l) for i,l in lines_to_skip], footer=footer)
        
    
    
    def guess_comment_symbol(self, ifp):
        try:
            common_choices = ('#',';','%','//')
            counts = [0,0,0,0]
            
            for line in ifp:
                for i in range(len(counts)):
                    if line.lstrip().startswith(common_choices[i]):
                        counts[i] += 1
                        break
        finally:
            ifp.seek(0)
        if max(counts) == 0:
            return None
        return common_choices[counts.index(max(counts))]
    
    
    def guess_number_of_columns(self, ifp):
        try:
            col_counts = {}
            
            for line in ifp:
                n_cols = len(line.split())
                if col_counts.has_key(n_cols):
                    col_counts[n_cols] += 1
                else:
                    col_counts[n_cols] = 1
            
            cols, counts = zip(*col_counts.items())
            counts, cols = multi_sort(counts, cols)
        finally:
            ifp.seek(0)
        
        return cols[-1]
    
    
    def guess_data_lines(self, ifp, n_cols, comment=None):
        try:
            lines = ifp.readlines()
            lines_to_skip = []
            start_idx = None
            end_idx = None
            for i, line in enumerate(lines):
                if comment is not None and line.startswith(comment):
                    if start_idx is not None:
                        lines_to_skip.append((i,line))
                    continue
                if len(line.split()) == n_cols:
                    if start_idx is None:
                        start_idx = i
                    else:
                        end_idx = i
                else:
                    lines_to_skip.append((i,line))
            if end_idx is None:
                end_idx = start_idx
            
            while lines_to_skip and lines_to_skip[-1][0] >= end_idx:
                lines_to_skip.pop() #otherwise it will include line=end_idx
            
            
        finally:
            ifp.seek(0)
            
        return start_idx, end_idx, lines_to_skip
    
    
    def get_columns(self, ifp, n_cols, start_idx, end_idx, lines_to_skip, headings):
        
        columns = []
        for i in range(n_cols):
            columns.append([])
        
        lines = ifp.readlines()
        ifp.seek(0)
        
        header = ''.join(lines[:start_idx])
        
        if len(lines) == end_idx + 1:
            footer=''
        else:
            footer = ''.join(lines[end_idx+1:])
        
        lines = lines[start_idx:end_idx+1]
        for idx in [i[0]-start_idx for i in reversed(sorted(lines_to_skip, cmp=tuple_compare))]:
            lines.pop(idx)
        
        for line in lines:
            vals = line.split()
            
            for i in range(n_cols):
                columns[i].append(vals[i])

        return header,[loader.ColumnData(c, title=headings[i]) for i,c in enumerate(columns)],footer
        
           
    def guess_column_titles(self, ifp, n_cols, start_idx, comment_symbol):
        if start_idx == 0:
            #there are no column headings - data starts in the first row
            return ['']*n_cols
        
        lines = ifp.readlines()
        ifp.seek(0)
        
        words = lines[start_idx - 1].lstrip(comment_symbol).split()
        if len(words) == n_cols:
            return words
        elif len(words) < n_cols:
            #it cannot be column titles
            return ['']*n_cols
        else:
            #life is more difficult since the column names might have spaces in them
            #first check to see if there are a sane number of separators greater than one space
            line = lines[start_idx - 1].strip().lstrip(comment_symbol).lstrip()
            
            seps = re.findall(r' {2,}| ?[\t\n\r\f\v]+', line)
            
            if len(seps) != n_cols - 1:
                return ['']*n_cols

            names = []
            for s in seps:
                name,line = line.split(s, 1)
                names.append(name)
            names.append(line)
            
            if len(names) == n_cols:
                return names
            else:
                return ['']*n_cols


        
loader.register_loader(TextFileLoader())        