import magic
import wx
import re
import StringIO
import os.path
from std_ops.iter_ import multi_sort, tuple_compare
from avoplot.plugins import AvoPlotPluginBase
from avoplot.persist import PersistantStorage
from column_selector import TxtFileDataSeriesSelectFrame
#from avoplot.plugins.avoplot_fromfile_plugin.loader import FileLoaderBase
import loader
def load(filename):
    with open(filename,'rb') as ifp:
        s = ifp.read()
    return StringIO.StringIO(s)

class TextFilePlugin(AvoPlotPluginBase):
    def __init__(self):
        AvoPlotPluginBase.__init__(self, "Text File")
        
        
    def get_onNew_handler(self):
        return ("From file", "", "Plot data from a file", self.on_new)
    
    
    def on_new(self,evnt):
        persistant_storage = PersistantStorage()
        
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
            plt = series_select_dialog.get_plot()
            self.add_plot_to_main_window(plt)
        
        
class TextFileLoader(loader.FileLoaderBase):
    
    def __init__(self):
        self.name = "Text file loader"
        
        
    def test(self, filename, ifp):
        
        try:
            file_type = magic.from_buffer(ifp.read(),mime=True)
        except Exception, e:
            print e.args
            return False
        finally:
            ifp.seek(0)
        print file_type
        if file_type.startswith('text/'):
            return True
        else:
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
            
            print "Data ranges from line %d to line %d"%(start_idx, end_idx)
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
            print "popped",lines.pop(idx)
        
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