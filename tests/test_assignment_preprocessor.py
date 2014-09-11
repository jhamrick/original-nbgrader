from IPython.nbformat.current import read as read_nb
from IPython.nbformat.current import NotebookNode
from nbgrader import AssignmentPreprocessor


class TestAssignmentPreprocessor(object):

    def setup(self):
        with open("tests/files/test.ipynb", "r") as fh:
            self.nb = read_nb(fh, 'ipynb')
        self.cells = self.nb.worksheets[0].cells
        self.preprocessor = AssignmentPreprocessor()

    def test_get_assignment_cell_type_default(self):
        """Is the cell type '-' when the assignment metadata is missing?"""
        cell = NotebookNode()
        cell.metadata = {}
        cell_type = self.preprocessor._get_assignment_cell_type(cell)
        assert cell_type == '-'

    def test_get_assignment_cell_type_given(self):
        """Is the cell type correct when the assignment metadata is present?"""
        cell = NotebookNode()
        cell.metadata = dict(assignment=dict(cell_type="foo"))
        cell_type = self.preprocessor._get_assignment_cell_type(cell)
        assert cell_type == "foo"

    def test_concatenate_nothing(self):
        """Are the cells the same if there is no header/footer?"""
        cells = self.preprocessor._concatenate_notebooks(self.cells)
        assert cells == self.cells

    def test_concatenate_header(self):
        """Is the header prepended correctly?"""
        self.preprocessor.header = "tests/files/test.ipynb"
        cells = self.preprocessor._concatenate_notebooks(self.cells[:-1])
        assert cells == (self.cells + self.cells[:-1])

    def test_concatenate_footer(self):
        """Is the footer appended correctly?"""
        self.preprocessor.footer = "tests/files/test.ipynb"
        cells = self.preprocessor._concatenate_notebooks(self.cells[:-1])
        assert cells == (self.cells[:-1] + self.cells)

    def test_concatenate_header_and_footer(self):
        """Is the header and footer concatenated correctly?"""
        self.preprocessor.header = "tests/files/test.ipynb"
        self.preprocessor.footer = "tests/files/test.ipynb"
        cells = self.preprocessor._concatenate_notebooks(self.cells[:-1])
        assert cells == (self.cells + self.cells[:-1] + self.cells)

    def test_filter_solution(self):
        """Are release and skip cells filtered out when solution=True?"""
        self.preprocessor.solution = True
        cells = self.preprocessor._filter_cells(self.cells)
        for cell in cells:
            cell_type = self.preprocessor._get_assignment_cell_type(cell)
            assert cell_type != 'skip'
            assert cell_type != 'release'

    def test_filter_release(self):
        """Are solution and skip cells filtered out when solution=False?"""
        self.preprocessor.solution = False
        cells = self.preprocessor._filter_cells(self.cells)
        for cell in cells:
            cell_type = self.preprocessor._get_assignment_cell_type(cell)
            assert cell_type != 'skip'
            assert cell_type != 'solution'
