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
import os.path
import numpy

from avoplot.persist import PersistentStorage
from avoplot.plugins import AvoPlotPluginSimple
from avoplot.subplots import AvoPlotXYSubplot
from avoplot.series import XYDataSeries

import xlrd
import os.path
import datetime
import re


def ExcelRowIter(filename):    
    book = xlrd.open_workbook(filename)    
    if book.nsheets > 1:
        print "Warning: File contains more than one sheet - I'm assuming you want the first one."    
    sh = book.sheet_by_index(0)    
    for i in range(sh.nrows):
        yield sh.row_values(i)

def load_adv_retrieval_file(adv_ret_xls_file):
    
    filenames=[]
    times = []
    col_amounts = []
    errors = []
    
    #read the date from the directory that the columns file is in (the date is not stored
    #in the file
    parent_folder = os.path.split(os.path.dirname(os.path.realpath(adv_ret_xls_file)))[-1]
    
    #use regular expression to extract date information
    r = re.match("(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})", parent_folder)
    if r is None:
        raise RuntimeError, "Failed to extract the date from the parent folder."
    
    date_info = r.groupdict()
    record_date = datetime.datetime(int(date_info['year']),int(date_info['month']), int(date_info['day']))
    
    
    data_reader = ExcelRowIter(adv_ret_xls_file)
                    
    #read the rows up to the one containing the column headings and record
    #the column headings
    #skip the first row
    data_reader.next()
    i=0
    missing_files = []
    for row in data_reader:
        if row[3].isspace() or row[3] == "":
            continue
        
        #sometimes the times column is formatted in such a way that it is read as fractional hours since 00:00:00
        #instead of a string
        try:
            times.append(record_date + datetime.timedelta(hours = 24 * float(row[5])))
        except ValueError:
            times.append(datetime.datetime.combine(record_date.date(),datetime.datetime.strptime(row[5],"%H:%M:%S").time()))
        
        filenames.append(row[3])
        if int(row[4]) != i:
            print "Warning: Spectrum number",i,"is missing from the advanced retrieval results!"
            missing_files.append(i)
            i= int(row[4])
        col_amounts.append(float(row[8]))
        errors.append(float(row[9]))
        i+=1    
    #if the times went passed midnight then we have a problem (because the date will not have changed accordingly)
    #to fix this we just look for large backwards steps in the times and add an extra day as appropriate
    i=1
    while i<len(times):
        if times[i]<times[i-1]:
            times[i] += datetime.timedelta(days=1)
        i+=1
    
    return filenames, times, col_amounts, errors





plugin_is_GPL_compatible = True


class DOASAdvRetSubplot(AvoPlotXYSubplot):
    def my_init(self):
        ax = self.get_mpl_axes()
        ax.set_xlabel('Time')
        ax.set_ylabel('SO$_2$ (ppm m)')
    

#define new data series type for DOAS data
class DOASAdvRetData(XYDataSeries):
    @staticmethod
    def get_supported_subplot_type():
        return DOASAdvRetSubplot


class DOASAdvRetPlugin(AvoPlotPluginSimple):
    def __init__(self):
        AvoPlotPluginSimple.__init__(self,"DOAS Advanced Retrieval  Plugin", DOASAdvRetData)
        
        self.set_menu_entry(['DOAS','Advanced Retrieval'], "Plot a DOAS Advanced Retrieval File")
    
    
    def plot_into_subplot(self, subplot):
        filename,times,cas = self.load_spectrum()
        
        if filename is None:
            return False
        
        data_series = DOASAdvRetData(os.path.basename(filename),
                                       xdata=numpy.array(times), 
                                       ydata=numpy.array(cas))
        
        subplot.add_data_series(data_series)
        
        return True
    
    
    def load_spectrum(self):
        persist = PersistentStorage()
        
        try:
            last_path_used = persist.get_value("doas_adv_ret_dir")
        except KeyError:
            last_path_used = ""
        
        #get filename to open
        adv_ret_file = wx.FileSelector("Choose advanced retrieval file to open", 
                                        default_path=last_path_used)
        if adv_ret_file == "":
            return None,None,None
        
        persist.set_value("doas_adv_ret_dir", os.path.dirname(adv_ret_file))
        
        try:        
            
            filenames, times, col_amounts, errors = load_adv_retrieval_file(adv_ret_file)
            return adv_ret_file, times, col_amounts
        except Exception,e:
            print e.args
            wx.MessageBox("Unable to load adv ret file \'%s\'. "%adv_ret_file, 
                          "AvoPlot", wx.ICON_ERROR)
            return None,None,None


