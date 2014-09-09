c = get_config()

c.NbConvertApp.export_format = 'notebook'
c.NbConvertApp.writer_class = 'nbgrader.AssignmentWriter'

c.Exporter.preprocessors = ['nbgrader.AssignmentPreprocessor']

c.AssignmentPreprocessor.title = 'Example Assignment'
c.AssignmentPreprocessor.header = 'header.ipynb'
