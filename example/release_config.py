c = get_config()

c.NbConvertApp.notebooks = ['Assignment Template.ipynb']
c.NbConvertApp.output_base = 'Assignment'
c.NbConvertApp.export_format = 'notebook'

c.Exporter.preprocessors = ['preprocessor.ReleasePreprocessor']

c.ReleasePreprocessor.solution = False
c.ReleasePreprocessor.title = 'Example Assignment'
