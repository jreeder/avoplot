from avoplot.plugins import setup

setup(name='UV-VIS Plugin',
      version='0.0.1',
      description='AvoPlot plugin for analysing UV-VIS spectrum', 
      author = 'Kayla Iacovino', 
      author_email='kaylaiacovino@gmail.com',
      package_dir = {'':'src'},
      packages=['UV-VIS_plugin']
      )