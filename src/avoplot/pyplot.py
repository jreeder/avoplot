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
import multiprocessing
from multiprocessing import connection 
import subprocess
import threading
import sys
import traceback
from StringIO import StringIO

import wx
import avoplot.gui.main
from avoplot import series
from avoplot import subplots
import avoplot.figure



class _PyplotXYDataSeries(series.XYDataSeries):
    def __init__(self, plot_args, plot_kwargs, xdata=None, ydata=None):
        self.__plot_args = plot_args #not including data
        self.__plot_kwargs = plot_kwargs
        series.XYDataSeries.__init__(self, 'series', xdata=xdata, ydata=ydata)
    
    
    def plot(self, subplot):
        return subplot.get_mpl_axes().plot(*(self.get_data()+self.__plot_args), 
                                           **self.__plot_kwargs)



def _get_current_fig_number():
    pass

#TODO - exceptions in the remote instance should be passed back and raised by 
#the proxy

CMD_RECV_ACKNOWLEDGEMENT = 'cmd_ack'

class CommunicationError(IOError):
    pass



class _AvoPlotPyplotCommand:
    def __init__(self, cmd_name, args, kwargs):
        
        self.cmd_name = cmd_name
        self.args = args
        self.kwargs = kwargs
        


class _RemoteException:
    def __init__(self, type_, value, tb):
        self.ex = type_("".join(traceback.format_exception(*sys.exc_info())))
        
        self.type = type_
        self.value = value
        
        s = StringIO()
        traceback.print_tb(tb, file=s)
        
        self.traceback_str = s.getvalue()
    
    def raise_exc(self):
        raise self.type, ''.join([str(self.value), self.traceback_str])
        #raise self.type, "".join(["", self.traceback_str]), None 


class _AvoPlotRemoteInstance:
    def __init__(self, port, auth_key):
        self._cmd_method_mapping = {
                                    'plot': self._plot,
                                    'show': self._show,
                                    'figure': self._figure,
                                    'xlabel': self._xlabel,
                                    'ylabel': self._ylabel,
                                    'title': self._title
                                    }
        
        self._cur_avoplot_fig = None
        self._cur_avoplot_subplot = None
        
        
        self.__connection = connection.Client(('localhost',port), authkey=auth_key)
        self.__recv_thread = threading.Thread(target=self.__listen_for_commands)
        
        #create the AvoPlot instance
        self.app = avoplot.gui.main.AvoPlotApp((), (), start_hidden=True)
        
        #start receiving commands
        self.__recv_thread.start()
        
        #enter the app's mainloop
        self.app.MainLoop()
        
        #if we get here then the program has been closed - tidy up and exit
        self._exit()
    
    
    def _get_cur_avoplot_fig(self):
        
        parent = self.app.GetTopWindow()
        
        #check if the figure has been closed by the user by seeing if it still
        #exists in the session (the parent element for all figures)
        if not self._cur_avoplot_fig in parent.session.get_child_elements():
            self._cur_avoplot_fig = None
        
        if self._cur_avoplot_fig is None:
            fig = avoplot.figure.AvoPlotFigure(parent,'Figure')
            parent.add_figure(fig)
            self._cur_avoplot_fig = fig
            
        return self._cur_avoplot_fig
    
    
    def _get_cur_avoplot_subplot(self):
        #check that the figure containing the subplot still exists - it might
        #have been closed by the user
        if (self._cur_avoplot_subplot is not None and 
            self._get_cur_avoplot_fig() != self._cur_avoplot_subplot.get_figure()):
            
            self._cur_avoplot_subplot = None
        
        #even if the figure still exists, the subplot may have been closed - 
        #check to see if it is still a child of the figure
        if (self._cur_avoplot_subplot is not None and 
            not self._cur_avoplot_subplot in self._cur_avoplot_fig.get_child_elements()):
            self._cur_avoplot_subplot = None
        
        #if there is no current subplot, then create one in the current figure
        if self._cur_avoplot_subplot is None:
            subplot = subplots.AvoPlotXYSubplot(self._get_cur_avoplot_fig(), 'Subplot')
            self._cur_avoplot_subplot = subplot
        
        return self._cur_avoplot_subplot
    
    
    def _exit(self):
        #stop receiving commands from the proxy
        self.__connection.close()
        self.__recv_thread.join()
        
        
    def __listen_for_commands(self):
        
        #this loop gets broken when self.exit() gets called since the 
        #connection will get closed causing the recv() call to raise an 
        #EOF exception and exit the thread
        while True:
            try:
                cmd = self.__connection.recv()
            
            except EOFError:
                return
            
            #try:
            try:
                wx.MutexGuiEnter()
                self.__execute_command(cmd)
            except:
                remote_ex = _RemoteException(*sys.exc_info())
                self.__connection.send(remote_ex)
                continue
            finally:
                wx.MutexGuiLeave()
            
            self.__connection.send(CMD_RECV_ACKNOWLEDGEMENT)
                
                
            #except Exception as ex:
            #    remote_ex = _RemoteException(ex)
            #    self.__connection.send(remote_ex)
            #    raise ex
            
     
    def __execute_command(self, cmd):
 
        func = self._cmd_method_mapping[cmd.cmd_name]
        func(cmd.args, cmd.kwargs)      
    
    
    def _plot(self, args, kwargs):
        subplot = self._get_cur_avoplot_subplot()
        
        for xdata, ydata, fmt_str in _split_plot_args(args):
            
            series = _PyplotXYDataSeries((fmt_str,), kwargs, xdata=xdata, ydata=ydata)
            subplot.add_data_series(series)
    
    
    def _show(self, args, kwargs):
        self.app.GetTopWindow().Show()
    
    
    def _figure(self, args, kwargs):
        
        parent = self.app.GetTopWindow()
        fig = avoplot.figure.AvoPlotFigure(parent,'Figure')
        parent.add_figure(fig)
        self._cur_avoplot_fig = fig
    
    
    def _xlabel(self, args, kwargs):
        subplot = self._get_cur_avoplot_subplot()
        ax = subplot.get_mpl_axes()
        ax.set_xlabel(*args, **kwargs)
    
    
    def _ylabel(self, args, kwargs):
        subplot = self._get_cur_avoplot_subplot()
        ax = subplot.get_mpl_axes()
        ax.set_ylabel(*args, **kwargs)
    
    
    def _title(self, args, kwargs):
        subplot = self._get_cur_avoplot_subplot()
        ax = subplot.get_mpl_axes()
        ax.set_title(*args, **kwargs)



def _split_plot_args(args):
    split_args = []
    tmp = []
    for a in args:
        tmp.append(a)
        if type(a) is str:
            split_args.append(tmp)
            tmp = []
    if tmp:
        split_args.append(tmp) 
               
    result = []
    for a in split_args:
        if type(a[0]) is str:
            raise ValueError
        
        if len(a) == 1:
            result.append((None, a[0], ''))
            
        elif len(a) == 2:
            if type(a[1]) is str:
                result.append((None, a[0], a[1]))
                
            else:
                result.append((a[0], a[1], ''))
                
        elif len(a) == 3:
            if type(a[1]) is str:
                raise ValueError
            
            if type(a[2]) is not str:
                raise ValueError
            
            result.append((a[0], a[1], a[2]))
        else:
            raise ValueError
    return result
            


class _AvoPlotRemoteInstanceProxy:
    def __init__(self):
        self.__connection = None
        self.__listener = None
        self.__failed_com_exception = None
        self.__failed_com_count = 0
        
        #generate an authentication key and convert it to a hex string (so that
        #it can easily be passed as a commandline argument)
        s = str(multiprocessing.current_process().authkey)
        self.__auth_key = ":".join("{0:x}".format(ord(c)) for c in s)
    
    
    def send_command(self, name, args, kwargs):
        cmd = _AvoPlotPyplotCommand(name, args, kwargs)
        
        self.__ensure_connection()
        try:
            self.__connection.send(cmd)
            
            #if the remote process has exited, then this will raise EOFError
            response = self.__connection.recv()
            
            if isinstance(response, _RemoteException):
                response.raise_exc()
               
            
            if response != CMD_RECV_ACKNOWLEDGEMENT:
                raise CommunicationError('Unexpected response from AvoPlot '
                                         'daemon - expecting \'%s\' but '
                                         'received \'%s\''%(CMD_RECV_ACKNOWLEDGEMENT,
                                                            str(response)))
            
            self.__failed_com_count = 0
            
        except (EOFError, IOError, CommunicationError) as self.__failed_com_exception:
            #something has gone wrong! Tidy up the open sockets and try again.
            #Note that trying again will open a new remote process (we assume 
            #that the old one has crashed somehow)
            self.__failed_com_count += 1
            self.__connection.close()
            if self.__listener is not None:
                self.__listener.close()
                
            self.__connection = None
            self.__listener = None
            
            #try again
            self.send_command(name, args, kwargs)
    
    
    def __ensure_connection(self):
        if self.__failed_com_count >= 5:
            raise CommunicationError("Failed to connect to AvoPlot daemon process."
                                  " Final attempt to reconnect failed with "
                                  "error: \'%s\'"%(str(self.__failed_com_exception)))
        
        if self.__connection is None:
            
            #find a free port to open the connection on (starting at 25000 and 
            #working upwards)
            port = 25000
            while True:
                try:
                    self.listener = connection.Listener(('localhost', port), 
                                                        authkey=self.__auth_key)
                    break
                except:
                    port += 1
            
            #start a new AvoPlot instance in a separate process
            subprocess.Popen([sys.executable, '-c', 'from avoplot import pyplot;'
                              ' pyplot._AvoPlotRemoteInstance(%s, \"%s\")'%(port, self.__auth_key)], close_fds=True)
            
            #connect to the avoplot process
            self.__connection = self.listener.accept()
            
        


#create a single instance of the proxy            
__avoplot_remote_instance_proxy = _AvoPlotRemoteInstanceProxy()
 

def plot(*args, **kwargs):
    __avoplot_remote_instance_proxy.send_command('plot', args, kwargs)


def show():
    __avoplot_remote_instance_proxy.send_command('show', (), {})


def figure(*args, **kwargs):
    __avoplot_remote_instance_proxy.send_command('figure', args, kwargs)


def xlabel(s, *args, **kwargs):
    __avoplot_remote_instance_proxy.send_command('xlabel', (s,) + args, kwargs)
    

def ylabel(s, *args, **kwargs):
    __avoplot_remote_instance_proxy.send_command('ylabel', (s,) + args, kwargs)
    

def title(s, *args, **kwargs):    
    __avoplot_remote_instance_proxy.send_command('title', (s,) + args, kwargs)
    
    