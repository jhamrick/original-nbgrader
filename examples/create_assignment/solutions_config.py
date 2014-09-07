import os

c = get_config()

c.NbConvertApp.notebooks = ['Assignment Template.ipynb']
c.NbConvertApp.output_base = 'Assignment Solution'
c.NbConvertApp.export_format = 'html'

c.Exporter.preprocessors = ['nbgrader.ReleasePreprocessor']
c.Exporter.template_file = "solutions"
c.Exporter.template_path = [os.path.dirname(os.path.realpath(__file__))]

c.ReleasePreprocessor.solution = True
c.ReleasePreprocessor.title = 'Example Assignment'
c.ReleasePreprocessor.resource_path = os.path.dirname(os.path.realpath(__file__))
c.ReleasePreprocessor.header = 'header.ipynb'
