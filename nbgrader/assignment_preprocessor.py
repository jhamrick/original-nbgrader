from jinja2 import Environment
from IPython.nbconvert.preprocessors import ExecutePreprocessor
from IPython.utils.traitlets import Bool, Unicode
from IPython.nbformat.current import read as read_nb

from . import util


class AssignmentPreprocessor(ExecutePreprocessor):

    solution = Bool(
        False, config=True,
        info_test="Whether to generate the release version, or the solutions")

    header = Unicode("", config=True, info_test="Path to header notebook")
    footer = Unicode("", config=True, info_test="Path to footer notebook")
    title = Unicode("", config=True, info_test="Title of the assignment")
    disable_toolbar = Bool(
        True, config=True,
        info_test="Whether to hide the assignment toolbar after conversion")
    hide_autograder_cells = Bool(
        True, config=True,
        info_test="Whether to hide autograder cells after conversion")

    def __init__(self, *args, **kwargs):
        super(AssignmentPreprocessor, self).__init__(*args, **kwargs)
        self.env = Environment(
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=False)

    def preprocess(self, nb, resources):
        cells = []

        # header
        if self.header != "":
            with open(self.header, 'r') as fh:
                header_nb = read_nb(fh, 'ipynb')
            cells.extend(header_nb.worksheets[0].cells)

        # body
        cells.extend(nb.worksheets[0].cells)

        # footer
        if self.footer != "":
            with open(self.footer, 'r') as fh:
                footer_nb = read_nb(fh, 'ipynb')
            cells.extend(footer_nb.worksheets[0].cells)

        # filter out various cells
        nb.worksheets[0].cells = self.filter_cells(cells)

        # remove the cell toolbar, if it exists
        if "celltoolbar" in nb.metadata:
            del nb.metadata['celltoolbar']

        # get the table of contents
        self.toc = util.get_toc(cells)

        # mark in the notebook metadata whether it's a solution or not
        nb.metadata['disable_assignment_toolbar'] = self.disable_toolbar
        nb.metadata['hide_autograder_cells'] = self.hide_autograder_cells

        # figure out which tests go with which problems
        last_problem = None
        for cell in nb.worksheets[0].cells:
            if 'assignment' not in cell.metadata:
                continue

            cell_type = cell.metadata['assignment']['cell_type']
            if cell_type == "grade":
                last_problem = cell
            elif cell_type == "autograder":
                if not last_problem:
                    raise RuntimeError(
                        "autograding cell before any gradeable cells!")

                if 'tests' not in last_problem.metadata['assignment']:
                    last_problem.metadata['assignment']['tests'] = []

                cell_id = cell.metadata['assignment']['id']
                last_problem.metadata['assignment']['tests'].append(cell_id)

        if self.solution:
            nb, resources = super(AssignmentPreprocessor, self).preprocess(
                nb, resources)
        else:
            nb, resources = super(ExecutePreprocessor, self).preprocess(
                nb, resources)

        return nb, resources

    def filter_cells(self, cells):
        new_cells = []
        for cell in cells:
            meta = cell.metadata.get('assignment', {})
            cell_type = meta.get('cell_type', '-')
            if cell_type == 'skip':
                continue
            elif cell_type == 'release' and self.solution:
                continue
            elif cell_type == 'solution' and not self.solution:
                continue
            new_cells.append(cell)
        return new_cells

    def preprocess_cell(self, cell, resources, cell_index):
        kwargs = {
            "solution": self.solution,
            "toc": self.toc,
            "title": self.title
        }

        if cell.cell_type == 'code':
            template = self.env.from_string(cell.input)
            rendered = template.render(**kwargs)
            cell.outputs = []
            if 'prompt_number' in cell:
                del cell['prompt_number']
            if rendered[-1] == "\n":
                rendered = rendered[:-1]
            cell.input = rendered

        elif cell.cell_type in ('markdown', 'heading'):
            template = self.env.from_string(cell.source)
            rendered = template.render(**kwargs)
            if rendered[-1] == "\n":
                rendered = rendered[:-1]
            cell.source = rendered

        meta = cell.metadata.get('assignment', {})
        assignment_cell_type = meta.get('cell_type', '-')

        if assignment_cell_type == "autograder":
            if 'tests' not in resources:
                resources['tests'] = {}

            if meta['id'] in resources['tests']:
                raise ValueError(
                    "test id '{}' is used more than once".format(meta['id']))

            if cell.cell_type == 'code':
                resources['tests'][meta['id']] = cell.input
                if self.hide_autograder_cells:
                    cell.input = ""
            else:
                resources['tests'][meta['id']] = cell.source
                if self.hide_autograder_cells:
                    cell.source = ""

        elif assignment_cell_type == "grade":
            if 'rubric' not in resources:
                resources['rubric'] = {}
            resources['rubric'][meta['id']] = {
                "points": float(meta["points"]),
                "tests": meta.get("tests", [])
            }

        if self.solution:
            cell, resources = super(AssignmentPreprocessor, self)\
                .preprocess_cell(cell, resources, cell_index)

        return cell, resources
