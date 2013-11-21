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
import StringIO
import string
import datetime
import numpy

__available_loaders = []

class InvalidDataTypeError(TypeError):
    pass

def register_loader(loader_instance):
    __available_loaders.append(loader_instance)


def load_file(filename):
    import txt_file_loader
    
    with open(filename,'rb') as ifp:
        s = ifp.read()
    ifp = StringIO.StringIO(s)
    flag=False
    for loader in __available_loaders:
        
        flag = loader.test(filename, ifp)
        if flag:
            break
    if flag:
        return loader.load(filename, ifp)
    raise IOError('Cannot load the file %s'%filename)


class FileLoaderBase:
    
    def test(self, filename, ifp):
        return False
    
    def load(self,filename, ifp):
        raise NotImplementedError


class FileContents:
    def __init__(self, filename, columns, header=None, comment_symbols=[], skipped_rows=[], footer=None):
        self.filename = filename
        self.header = header
        self.__columns = columns
        self.comment_symbols = comment_symbols
        self.skipped_rows = skipped_rows
        self.footer = footer
           
        #build mapping between column names and indices
        self.__col_name_mapping = {}
        for c in range(len(self.__columns)):
            self.__col_name_mapping[self.get_col_name(c)] = c
    
    
    def get_col_name(self, n):
        quotient=n+1 #want n=1 to yield 'A'
        indx = []
        while quotient > 0:  
            quotient = n // 26
            remainder = n % 26        
            indx.append(remainder)
            n = quotient
        for i in range(1,len(indx)):
            indx[i] -= 1        
        return ''.join([string.ascii_uppercase[i] for i in reversed(indx)])
    
    
    def get_column_by_index(self, idx):
        return self.__columns[idx]
    
    
    def get_column_by_name(self, name):
        idx = self.__col_name_mapping[name]
        return self.get_column_by_index(idx)
    
    
    def get_number_of_columns(self):
        return len(self.__columns)
    
    
    def get_number_of_rows(self):
        return self.__columns[0].get_number_of_rows()
    
    
    def get_columns(self):
        return self.__columns
    
    
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
    
    def get_data_mask(self):
        return self.get_data().mask

    
    def get_number_of_rows(self):
        return len(self.raw_data)
    
    
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
            self.d_type = 'number'
            return self.d_type
        
        self.d_type ='text'
        
#        is_time = 0
#        not_time = 0
#        for x in self.raw_data:
#            try:
#                datetime.datetime.strptime(x,"%H:%M:%S")
#                is_time += 1
#            except ValueError:
#                not_time += 1
#        if is_time > not_time:
#            self.d_type = 'time'
        
        return self.d_type
    
    
    def set_data_type(self, dtype):
        old_dtype = self.d_type
        self.data = None #force re-interpretation of the data
        self.d_type = dtype
        d = self.get_data()
        if len(d) > 0 and numpy.all(d.mask):
            self.d_type = old_dtype
            self.data = None
            raise InvalidDataTypeError
        
    
    
    def get_data(self):
        if self.data is not None:
            return self.data
        
        self.data = _converters[self.get_data_type()](self.raw_data)
        return self.data


def _float(s):
    try:
        return float(s)
    except ValueError:
        return numpy.nan
        
        
def to_float(data):
    return numpy.ma.masked_invalid([_float(i) for i in data])


def to_str(data):
    return numpy.ma.masked_array(data, mask=numpy.zeros_like(data))
   
   
_converters = {'number':to_float,
               'text':to_str}

    
    
    
    
    
            
    