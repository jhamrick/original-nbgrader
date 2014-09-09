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

    def __init__(self, *args, **kwargs):
        super(AssignmentPreprocessor, self).__init__(*args, **kwargs)
        self.env = Environment(trim_blocks=True, lstrip_blocks=True)

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

        # figure out what the headings are for each cell
        util.mark_headings(cells)

        # get the table of contents
        self.toc = util.get_toc(cells)

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
        if cell.cell_type == 'code':
            template = self.env.from_string(cell.input)
            cell.input = template.render(solution=self.solution)
            cell.outputs = []
            if 'prompt_number' in cell:
                del cell['prompt_number']

        elif cell.cell_type == 'markdown':
            template = self.env.from_string(cell.source)
            cell.source = template.render(solution=self.solution, toc=self.toc)

        elif cell.cell_type == 'heading':
            template = self.env.from_string(cell.source)
            cell.source = template.render(solution=self.solution)

        if self.solution:
            cell, resources = super(AssignmentPreprocessor, self)\
                .preprocess_cell(cell, resources, cell_index)

        return cell, resources
