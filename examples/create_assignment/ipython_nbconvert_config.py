c = get_config()

c.NbConvertApp.export_format = 'notebook'

c.Exporter.preprocessors = ['nbgrader.ReleasePreprocessor']
c.ReleasePreprocessor.title = 'Example Assignment'
c.ReleasePreprocessor.header = 'header.ipynb'
