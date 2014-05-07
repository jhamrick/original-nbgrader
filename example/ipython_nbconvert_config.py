c = get_config()

c.NbConvertApp.notebooks = ['test1.ipynb']
c.NbConvertApp.output_base = 'test1_graded'
c.NbConvertApp.export_format = 'notebook'

c.Exporter.preprocessors = ['nbgrader.Grader']

c.InteractiveShellApp.exec_lines = []

c.Grader.assignment = "test1"
c.Grader.autograder = "test1_autograder.py"
c.Grader.heading_level = 1