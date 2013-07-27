
Installation
============

Prerequisites
-------------

AvoPlot depends on several other software packages that you will need to install before installing AvoPlot. Instructions for installing the prerequisites can be found on their respective home pages. AvoPlot requires the following software to be installed:
  * wxPython_
  * NumPy_
  * matplotlib_
  
It is also recommended to install python-magic_, but given how difficult it is to get this to work on non-Linux systems, it is optional and AvoPlot will work without it.


.. _wxPython: http://www.wxpython.org/
.. _NumPy: http://www.numpy.org/
.. _matplotlib: http://matplotlib.org/
.. _python-magic: https://github.com/ahupp/python-magic
.. _repository: http://code.google.com/p/avoplot/source/checkout
.. _InkScape: http://inkscape.org/


Windows
-------

Download the Windows installer program from the downloads page (linked from `here <http://avoplot.googlecode.com>`_) and run it. The main AvoPlot program (AvoPlot.py) will be installed into the "Scripts" folder of your Python installation and a Start menu entry should be created for it.


Linux
-----

Download the tar.gz file from the downloads page (linked from `here <http://avoplot.googlecode.com>`_). Unpack the archive::
  
    tar -xzf AvoPlot-13.07.tar.gz

Change into the unpacked folder::
  
    cd AvoPlot-13.07

Then build and install using Python::
  
    python setup.py build
    python setup.py install

The second of these commands might require root/admin rights.
  

From SVN
--------

For the very latest version of AvoPlot, you can check-out the source tree from the SVN repository_.

The commands given in these instructions are for installation under Linux. It is assumed that if you are trying to install AvoPlot from SVN that you know what you are doing enough to be able to adapt the commands for your specific operating system!

Installing AvoPlot from source requires that you have InkScape_ installed on you computer in addition to the prerequisites listed above. This is used to generate the PNG icons for AvoPlot from their SVG versions. Furthermore, the InkScape_ executable must be on your system path.

  #. Check out the latest version of the code from the repository_. You can do this using the following command::

       svn checkout http://avoplot.googlecode.com/svn/trunk/ avoplot-read-only
  
  #. Create the AvoPlot icons::
       
       cd avoplot-read-only/icons
       python create_sized_icons.py
       
  #. Build and install the main program::
       
       cd ..
       python setup.py build
       sudo python setup.py install
       

