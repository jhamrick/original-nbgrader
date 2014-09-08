from jinja2 import Environment
from IPython.nbconvert.preprocessors import ExecutePreprocessor
from IPython.utils.traitlets import Bool, Unicode
from IPython.nbformat.current import read as read_nb


class ReleasePreprocessor(ExecutePreprocessor):

    solution = Bool(
        False, config=True,
        info_test="Whether to generate the release version, or the solutions")

    header = Unicode("", config=True, info_test="Path to header notebook")
    footer = Unicode("", config=True, info_test="Path to footer notebook")

    def __init__(self, *args, **kwargs):
        super(ReleasePreprocessor, self).__init__(*args, **kwargs)
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

        nb.worksheets[0].cells = cells

        if "celltoolbar" in nb.metadata:
            del nb.metadata['celltoolbar']

        # filter out various cells
        cells = []
        for cell in nb.worksheets[0].cells:
            meta = cell.metadata.get('assignment', {})
            cell_type = meta.get('cell_type', '-')
            if cell_type == 'skip':
                continue
            elif cell_type == 'release' and self.solution:
                continue
            elif cell_type == 'solution' and not self.solution:
                continue
            cells.append(cell)
        nb.worksheets[0].cells = cells

        # get the table of contents
        self.toc = self._get_toc(cells)

        if self.solution:
            nb, resources = super(ReleasePreprocessor, self).preprocess(
                nb, resources)
        else:
            nb, resources = super(ExecutePreprocessor, self).preprocess(
                nb, resources)

        return nb, resources

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

        elif cell.cell_type == 'header':
            template = self.env.from_string(cell.source)
            cell.source = template.render(solution=self.solution)

        if self.solution:
            try:
                cell, resources = super(ReleasePreprocessor, self)\
                    .preprocess_cell(cell, resources, cell_index)
            except:
                import ipdb; ipdb.set_trace()

        return cell, resources

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
