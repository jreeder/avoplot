from avoplot.plugins import setup

setup(name='AvoPlot FTIR Plugin',
      version='0.0.1',
      description='AvoPlot plugin for analysing FTIR spectrum', 
      author = 'Nial Peters', 
      author_email='nonbiostudent@hotmail.com',
      package_dir = {'':'src'},
      packages=['avoplot_ftir_plugin']
      )