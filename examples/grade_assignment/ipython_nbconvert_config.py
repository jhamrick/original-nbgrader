c = get_config()

c.NbConvertApp.notebooks = ['Submitted Assignment.ipynb']
c.NbConvertApp.output_base = 'Graded Assignment'
c.NbConvertApp.export_format = 'notebook'

c.Exporter.preprocessors = ['nbgrader.Grader']

c.InteractiveShellApp.exec_lines = []

c.Grader.assignment = "Assignment"
c.Grader.autograder_file = "example_autograder.py"
c.Grader.scores_file = "scores.json"
c.Grader.heading_level = 1
