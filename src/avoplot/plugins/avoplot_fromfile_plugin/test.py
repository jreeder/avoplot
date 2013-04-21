import loader
import datetime

st = datetime.datetime.now()
filename = "/home/nialp/Desktop/test_data"
#filename = '/home/nialp/Desktop/scan1/Processed/20120208/8feb_scan1__column.txt'
contents = loader.load_file(filename)
contents.print_summary()
et = datetime.datetime.now()

print "Loaded file in %s"%(et-st)
