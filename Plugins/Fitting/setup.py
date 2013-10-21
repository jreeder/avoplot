from avoplot.plugins import setup

setup(name='AvoPlot FittingPlugin',
      version='0.0.1',
      description='AvoPlot plugin for Fitting Data', 
      author = 'Kayla Iacovino',
      author_email = 'me@kaylaiacovino.com',
      package_dir = {'':'src'},
      packages=['fitting_plugin']
      )