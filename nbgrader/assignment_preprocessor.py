import json
from jinja2 import Environment
from IPython.nbconvert.preprocessors import ExecutePreprocessor
from IPython.utils.traitlets import Bool, Unicode
from IPython.nbformat.current import read as read_nb


class AssignmentPreprocessor(ExecutePreprocessor):

    solution = Bool(False, config=True, help="Whether to generate the release version, or the solutions")

    header = Unicode("", config=True, help="Path to header notebook")
    footer = Unicode("", config=True, help="Path to footer notebook")

    title = Unicode("", config=True, help="Title of the assignment")

    disable_toolbar = Bool(True, config=True, help="Whether to hide the assignment toolbar after conversion")
    hide_autograder_cells = Bool(True, config=True, help="Whether to hide autograder cells after conversion")

    rubric_file = Unicode("rubric", config=True, help="Filename to write JSON rubric to")
    autograder_tests_file = Unicode("autograder_tests", config=True, help="Filename to write JSON autograder tests to")

    def __init__(self, *args, **kwargs):
        super(AssignmentPreprocessor, self).__init__(*args, **kwargs)

        # create the jinja templating environment
        self.env = Environment(
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=False)

    def _concatenate_notebooks(self, cells):
        """Concatenates the cells from the header and footer notebooks to the
        given cells.

        """
        new_cells = []

        # header
        if self.header != "":
            with open(self.header, 'r') as fh:
                header_nb = read_nb(fh, 'ipynb')
            new_cells.extend(header_nb.worksheets[0].cells)

        # body
        new_cells.extend(cells)

        # footer
        if self.footer != "":
            with open(self.footer, 'r') as fh:
                footer_nb = read_nb(fh, 'ipynb')
            new_cells.extend(footer_nb.worksheets[0].cells)

        return new_cells

    @staticmethod
    def _get_assignment_cell_type(cell):
        """Get the assignment cell type from the assignment metadata."""
        if 'assignment' not in cell.metadata:
            return '-'
        return cell.metadata['assignment']['cell_type']

    def _filter_cells(self, cells):
        """Filter out cells, depending on the value of `self.solution`:

        * always filter out 'skip' cells
        * if self.solution == True, then filter out 'release' cells
        * if self.release == True, then filter out 'solution' cells

        """
        new_cells = []
        for cell in cells:

            # get the cell type
            cell_type = self._get_assignment_cell_type(cell)

            # determine whether the cell should be included
            if cell_type == 'skip':
                continue
            elif cell_type == 'release' and self.solution:
                continue
            elif cell_type == 'solution' and not self.solution:
                continue
            else:
                new_cells.append(cell)

        return new_cells

    @staticmethod
    def _get_toc(cells):
        """Extract a table of contents from the cells, based on the headings
        in the cells."""

        # get the minimum heading level
        try:
            min_level = min(x.level for x in cells if x.cell_type == 'heading')
        except ValueError:
            min_level = 1

        toc = []
        for cell in cells:
            # skip non-heading cells
            if cell.cell_type != 'heading':
                continue

            # format the indentation and anchor link
            level = cell.level
            source = cell.source
            indent = "\t" * (level - min_level)
            link = '<a href="#{}">{}</a>'.format(
                source.replace(" ", "-"), source)
            toc.append("{}* {}".format(indent, link))

        toc = "\n".join(toc)
        return toc

    def _match_tests(self, cells):
        """Determine which tests correspond to which problems."""

        tests = {}
        rubric = {}

        last_problem = None
        last_problem_id = None

        for cell in cells:
            cell_type = self._get_assignment_cell_type(cell)

            # if it's a grading cell, then it becomes the most recent
            # problem (to assign the autograding tests to)
            if cell_type == "grade":
                last_problem = cell
                last_problem_id = last_problem.metadata['assignment']['id']

                if last_problem_id in rubric:
                    raise RuntimeError(
                        "problem '{}' already exists!".format(
                            last_problem_id))

                # extract the point value
                points = last_problem.metadata['assignment']['points']
                if points == '':
                    points = 0
                else:
                    points = float(points)

                # add the problem to the rubric
                rubric[last_problem_id] = {
                    'tests': [],
                    'points': points
                }

            # if it's an autograder cell, then we need to add it to
            # the list of tests for the last problem cell and record
            # it in the tests dictionary
            elif cell_type == "autograder":
                if not last_problem:
                    raise RuntimeError(
                        "autograding cell before any gradeable cells!")

                cell_id = cell.metadata['assignment']['id']
                if cell_id in tests:
                    raise RuntimeError(
                        "test id '{}' is used more than once".format(cell_id))

                # add the test to the tests dictionary
                tests[cell_id] = {
                    'weight': 1,
                    'problem': last_problem_id
                }

                # add the test to the list of tests for the problem
                rubric[last_problem_id]['tests'].append(cell_id)

        # now normalize the test weights so that the weights of all
        # tests for a particular problem sum to one.
        for problem in rubric:
            # the total number of points this problem is worth
            total_points = float(rubric[problem]['points'])

            # get the list of tests for this problem
            problem_tests = rubric[problem]['tests']

            # compute the normalizing constant for the weights
            normalizer = float(sum(
                [tests[t]['weight'] for t in problem_tests]))

            # update weights and points for each test
            for test in problem_tests:
                tests[test]['weight'] /= normalizer
                tests[test]['points'] = total_points * tests[test]['weight']

        return tests, rubric

    def _preprocess_nb(self, nb, resources):
        cells = nb.worksheets[0].cells

        # add in the header and the footer notebooks
        cells = self._concatenate_notebooks(cells)

        # filter out various cells
        cells = self._filter_cells(cells)

        # get the table of contents -- important that this happens
        # after adding in the header/footer and doing the filtering,
        # in case there are header cells that are added/removed
        self.toc = self._get_toc(cells)

        # figure out which tests go with which problems
        tests, rubric = self._match_tests(cells)
        resources['tests'] = tests
        resources['rubric'] = rubric

        # update the notebook with the new cells
        nb.worksheets[0].cells = cells

        # remove the cell toolbar, if it exists
        if "celltoolbar" in nb.metadata:
            del nb.metadata['celltoolbar']

        # mark in the notebook metadata whether it's a solution or not
        nb.metadata['disable_assignment_toolbar'] = self.disable_toolbar
        nb.metadata['hide_autograder_cells'] = self.hide_autograder_cells

        return nb, resources

    def _extract_outputs(self, resources):
        """Write out the rubric and tests if it's the solution version -- this
        should be in the correct format for FilesWriter (i.e., we need
        to dump to json strings since it writes files in binary
        format).

        """
        if self.solution:
            if 'outputs' not in resources:
                resources['outputs'] = {}

            rubric = resources['rubric']
            filename = self.rubric_file + ".json"
            resources['outputs'][filename] = json.dumps(rubric)

            tests = resources['tests']
            filename = self.autograder_tests_file + ".json"
            resources['outputs'][filename] = json.dumps(tests)

    def preprocess(self, nb, resources):
        nb, resources = self._preprocess_nb(nb, resources)

        if self.solution:
            nb, resources = super(AssignmentPreprocessor, self).preprocess(
                nb, resources)
        else:
            nb, resources = super(ExecutePreprocessor, self).preprocess(
                nb, resources)

        # extract rubric and tests
        self._extract_outputs(resources)

        return nb, resources

    def preprocess_cell(self, cell, resources, cell_index):
        kwargs = {
            "solution": self.solution,
            "toc": self.toc,
            "title": self.title
        }

        # render templates in code cells
        if cell.cell_type == 'code':
            template = self.env.from_string(cell.input)
            rendered = template.render(**kwargs)
            cell.outputs = []
            if 'prompt_number' in cell:
                del cell['prompt_number']
            if rendered[-1] == "\n":
                rendered = rendered[:-1]
            cell.input = rendered

        # render templates in markdown/heading cells
        elif cell.cell_type in ('markdown', 'heading'):
            template = self.env.from_string(cell.source)
            rendered = template.render(**kwargs)
            if rendered[-1] == "\n":
                rendered = rendered[:-1]
            cell.source = rendered

        # if it's an autograder cell, then record the source and then
        # clear it (so it's not visible to students)
        assignment_cell_type = self._get_assignment_cell_type(cell)
        if assignment_cell_type == "autograder":
            cell_id = cell.metadata['assignment']['id']

            if cell.cell_type == 'code':
                resources['tests'][cell_id]['source'] = cell.input
                if self.hide_autograder_cells:
                    cell.input = ""
            else:
                resources['tests'][cell_id]['source'] = cell.source
                if self.hide_autograder_cells:
                    cell.source = ""

        # if it's the solution version, execute the cell
        if cell.cell_type == 'code' and self.solution:
            cell, resources = super(AssignmentPreprocessor, self)\
                .preprocess_cell(cell, resources, cell_index)

        return cell, resources
