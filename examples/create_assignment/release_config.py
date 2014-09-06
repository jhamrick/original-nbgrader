import os

c = get_config()

c.NbConvertApp.notebooks = ['Assignment Template.ipynb']
c.NbConvertApp.output_base = 'Assignment'
c.NbConvertApp.export_format = 'notebook'

c.Exporter.preprocessors = ['nbgrader.ReleasePreprocessor']

c.ReleasePreprocessor.solution = False
c.ReleasePreprocessor.title = 'Example Assignment'
c.ReleasePreprocessor.resource_path = os.path.dirname(os.path.realpath(__file__))
c.ReleasePreprocessor.header = 'header.ipynb'
