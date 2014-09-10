c = get_config()

c.NbConvertApp.notebooks = ['Submitted Assignment.ipynb']
c.NbConvertApp.output_base = 'Graded Assignment'
c.NbConvertApp.export_format = 'notebook'

c.Exporter.preprocessors = ['nbgrader.Grader']

c.InteractiveShellApp.exec_lines = []

c.Grader.autograder_tests_file = "autograder_tests.json"
