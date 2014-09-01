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
import numpy
import math
import scipy.optimize
import scipy.stats
import collections


def get_fitting_tools():
    return __fitting_tools


class FittingError(Exception):
    """
    Exception raised when the fitting fails for some reason
    """
    pass



class FittingToolBase:
    def __init__(self, name):
        """
        Base class for fitting tools - must be subclassed.
        
        * name - a string describing the type of fit, this will be displayed in 
                 the drop-down menu.
        """
        
        self.name = name
        
        
    def fit(self, xdata, ydata):
        raise NotImplementedError("Subclasses should override the fit method of FittingToolBase")


class LinearFittingTool(FittingToolBase):
    def __init__(self):
        FittingToolBase.__init__(self, 'Linear')
    
    def fit(self, xdata, ydata):
        if len(xdata) != len(ydata):
            raise FittingError("Lengths of xdata and ydata must match")
        
        slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(xdata, ydata)
        
        fit_params = [("Linear Regression Results",''),
                      ("Gradient", slope),
                      ("Intercept",intercept),
                      ("R^2", r_value**2),
                      ("P value", p_value),
                      ("Std. Error", std_err)
                      ]
        
        fit_y_data = slope * xdata + intercept
        
        return xdata, fit_y_data, fit_params



class GaussianFittingTool(FittingToolBase):
    def __init__(self):
        FittingToolBase.__init__(self, 'Gaussian')
    
    
    def fit(self, xdata, ydata):
        return self.fit_gaussian(xdata, ydata)
    
        
    def fit_gaussian(self, xdata, ydata, amplitude_guess=None, mean_guess=None, 
                     sigma_guess=None, y_offset_guess=None, plot_fit=True):
        """
        Fits a gaussian to some data using a least squares fit method. Returns a named tuple
        of best fit parameters (amplitude, mean, sigma, y_offset).
         
        Initial guess values for the fit parameters can be specified as kwargs. Otherwise they
        are estimated from the data.
         
        If plot_fit=True then the fit curve is plotted over the top of the raw data and displayed.
        """
    
        if len(xdata) != len(ydata):
            raise FittingError("Lengths of xdata and ydata must match")
         
        if len(xdata) < 4:
            raise FittingError("xdata and ydata need to contain at least 4 elements each")
         
        # guess some fit parameters - unless they were specified as kwargs
        if amplitude_guess is None:
            amplitude_guess = max(ydata)
         
        if mean_guess is None:
            weights = ydata - numpy.average(ydata)
            weights[numpy.where(weights <0)]=0 
            mean_guess = numpy.average(xdata,weights=weights)
                        
        #use the y value furthest from the maximum as a guess of y offset 
        if y_offset_guess is None:
            data_midpoint = (xdata[-1] + xdata[0])/2.0
            if mean_guess > data_midpoint:
                yoffset_guess = ydata[0]        
            else:
                yoffset_guess = ydata[-1]
     
        #find width at half height as estimate of sigma        
        if sigma_guess is None:      
            variance = numpy.dot(numpy.abs(ydata), (xdata-mean_guess)**2)/numpy.abs(ydata).sum()  # Fast and numerically precise    
            sigma_guess = math.sqrt(variance)
         
         
        #put guess params into an array ready for fitting
        p0 = numpy.array([amplitude_guess, mean_guess, sigma_guess, yoffset_guess])
     
        #define the gaussian function and associated error function
        fitfunc = lambda p, x: p[0]*numpy.exp(-(x-p[1])**2/(2.0*p[2]**2)) + p[3]
        errfunc = lambda p, x, y: fitfunc(p,x)-y
        
        # do the fitting
        p1, success = scipy.optimize.leastsq(errfunc, p0, args=(xdata,ydata))
     
        if success not in (1,2,3,4):
            raise FittingError("Could not fit Gaussian to data.")
        
        xdata = numpy.linspace(xdata[0], xdata[-1], 2000)
        fit_y_data = [fitfunc(p1, i) for i in xdata]
         
        fit_params = [
                      ('Gaussian Fit Parameters',''),
                      ('Amplitude', p1[0]),
                      ('Mean',p1[1]),
                      ('Std. Dev.', p1[2]),
                      ('FWHM', 2.0 * math.sqrt(2.0 * math.log(2.0)) *p1[2]),
                      ('Y-offset', p1[3])
                      ]
        
        return xdata, fit_y_data, fit_params   





#all tools defined in this module must be added to this list in order to be
#accessible to AvoPlot
__fitting_tools = [LinearFittingTool(),GaussianFittingTool()]        