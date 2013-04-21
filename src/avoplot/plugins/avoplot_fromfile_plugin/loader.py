import StringIO
import datetime

__available_loaders = []


def register_loader(loader_instance):
    __available_loaders.append(loader_instance)


def load_file(filename):
    import txt_file_loader
    
    with open(filename,'rb') as ifp:
        s = ifp.read()
    ifp = StringIO.StringIO(s)
    flag=False
    for loader in __available_loaders:
        print "Trying %s"%loader.name
        flag = loader.test(ifp)
        if flag:
            break
    if flag:
        return loader.load(ifp)
    raise IOError('Cannot load the file %s'%filename)


class FileLoaderBase:
    
    def test(self, ifp):
        return False
    
    def load(self,ifp):
        raise NotImplementedError


class FileContents:
    def __init__(self, columns, header=None, comment_symbols=[], skipped_rows=[], footer=None):
        self.header = header
        self.columns = columns
        self.comment_symbols = comment_symbols
        self.skipped_rows = skipped_rows
    
    def print_summary(self):
        print "\n\n----------------------------------------"
        print "Comment symbols = %s"%self.comment_symbols
        print "File has %s columns of data"%len(self.columns)
        #print "Data is on lines %s-%s"%(start_idx,end_idx)
        print "Invalid data on lines %s"%[i for i,l in self.skipped_rows]
        for i,c in enumerate(self.columns):
            print "Column %d title = \'%s\', datatype = %s"%(i,c.title, c.get_data_type())
            
        print "----------------------------------------\n"


class ColumnData:
    def __init__(self, raw_data, title=''):
        self.raw_data = raw_data
        self.d_type = None
        self.data = None
        self.title = title
    
    
    def get_data_type(self):
        if self.d_type is not None:
            return self.d_type
        
        #first see if it is a float
        is_float = 0
        not_float = 0
        for x in self.raw_data:
            try:
                float(x)
                is_float += 1
            except ValueError:
                not_float += 1
        
        if is_float > not_float:
            self.d_type = 'float'
            return self.d_type
        
        self.d_type ='string'
        
        is_time = 0
        not_time = 0
        for x in self.raw_data:
            try:
                datetime.datetime.strptime(x,"%H:%M:%S")
                is_time += 1
            except ValueError:
                not_time += 1
        if is_time > not_time:
            self.d_type = 'time'
        
        return self.d_type
    
    
    def get_data(self, d_type=None):
        if self.data is not None:
            return self.data
        
        self.data = _converters[self.get_data_type()](self.raw_data)
        return self.data
        
    
_converters = {}

    
    
    
    
    
            
    