from avoplot.plugins import setup

setup(name='Kayla Test FTIR Plugin',
      version='0.0.1',
      description='AvoPlot plugin for analysing FTIR spectrum', 
      author = 'Kayla Iacovino', 
      author_email='kaylaiacovino@gmail.com',
      package_dir = {'':'src'},
      packages=['FTIR_plugin_kayla']
      )