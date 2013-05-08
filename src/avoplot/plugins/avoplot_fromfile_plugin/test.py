import loader
import datetime
import column_selector
import wx
from avoplot.gui.artwork import AvoplotArtProvider
app = wx.PySimpleApp()
#set up the icon for the frame
art_provider = AvoplotArtProvider()
wx.ArtProvider.Insert(art_provider)


st = datetime.datetime.now()
filename = "/home/nialp/Desktop/test_data"
#filename = '/home/nialp/Desktop/scan1/Processed/20120208/8feb_scan1__column.txt'
contents = loader.load_file(filename)
contents.print_summary()
column_selector.TxtFileDataSeriesSelectFrame(None, contents)
et = datetime.datetime.now()
app.MainLoop()
print "Loaded file in %s"%(et-st)
