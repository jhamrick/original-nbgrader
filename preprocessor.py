from jinja2 import Environment
from IPython.nbconvert.preprocessors import ExecutePreprocessor
from IPython.utils.traitlets import Bool, Unicode
from IPython.nbformat.current import new_code_cell, new_text_cell, \
    new_heading_cell

instructions = r"""Before you turn this problem in, make sure everything runs
as expected. First, **restart the kernel** (in the menubar, select
Kernel$\rightarrow$Restart) and then **run all cells** (in the
menubar, select Cell$\rightarrow$Run All).

Make sure you fill in any place that says `YOUR CODE HERE` or **YOUR
ANSWER HERE**, as well as your name and collaborators below:
"""

name_cell = """NAME = ""
COLLABORATORS = "" """


class ReleasePreprocessor(ExecutePreprocessor):

    solution = Bool(
        False, config=True,
        info_test="Whether to generate the release version, or the solutions")
    title = Unicode("", config=True, info_test="Title of the assignment")

    def __init__(self, *args, **kwargs):
        super(ReleasePreprocessor, self).__init__(*args, **kwargs)
        self.env = Environment(trim_blocks=True, lstrip_blocks=True)

    def preprocess(self, nb, resources):
        if self.solution:
            nb, resources = super(ReleasePreprocessor, self).preprocess(
                nb, resources)
        else:
            nb, resources = super(ExecutePreprocessor, self).preprocess(
                nb, resources)

        cells = nb.worksheets[0].cells
        toc = self._get_toc(cells)
        index = self._find_imports_cell(cells)

        index += 1
        cells.insert(index, new_heading_cell(
            source=self.title, level=1))

        index += 1
        cells.insert(index, new_text_cell(
            'markdown', source='---'))

        if toc:
            index += 1
            cells.insert(index, new_text_cell(
                'markdown', source=toc))

        if not self.solution:
            index += 1
            cells.insert(index, new_text_cell(
                'markdown', source=instructions))

            index += 1
            cells.insert(index, new_code_cell(
                input=name_cell))

        index += 1
        cells.insert(index, new_text_cell(
            'markdown', source='---'))

        if "celltoolbar" in nb.metadata:
            del nb.metadata['celltoolbar']

        return nb, resources

    def preprocess_cell(self, cell, resources, cell_index):
        if cell.cell_type == 'code':
            template = self.env.from_string(cell.input)
            cell.input = template.render(solution=self.solution)
            cell.outputs = []
            if 'prompt_number' in cell:
                del cell['prompt_number']

        elif cell.cell_type in ('markdown', 'heading'):
            template = self.env.from_string(cell.source)
            cell.source = template.render(solution=self.solution)

        if self.solution:
            try:
                cell, resources = super(ReleasePreprocessor, self).preprocess_cell(
                    cell, resources, cell_index)
            except:
                import ipdb; ipdb.set_trace()

        return cell, resources

    def _find_imports_cell(self, cells):
        i = 0
        while i < len(cells):
            if cells[i].metadata.get("imports", False):
                break
            i += 1
        if i == len(cells):
            i = -1
        return i

    def _get_toc(self, cells):
        headings = []
        for cell in cells:
            if cell.cell_type != 'heading':
                continue
            headings.append((cell.level, cell.source))

        if len(headings) == 0:
            return None

        min_level = min(x[0] for x in headings)
        toc = []
        for level, source in headings:
            indent = "\t" * (level - min_level)
            link = '<a href="#{}">{}</a>'.format(
                source.replace(" ", "-"), source)
            toc.append("{}* {}".format(indent, link))
        toc = "\n".join(toc)

        return toc
