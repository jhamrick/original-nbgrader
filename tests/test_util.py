from IPython.nbformat.current import NotebookNode
from nbgrader import util


def test_get_assignment_cell_type_default():
    """Is the cell type '-' when the assignment metadata is missing?"""
    cell = NotebookNode()
    cell.metadata = {}
    cell_type = util.get_assignment_cell_type(cell)
    assert cell_type == '-'


def test_get_assignment_cell_type_default2():
    """Is the cell type '-' when the assignment cell type is missing?"""
    cell = NotebookNode()
    cell.metadata = {'assignment': {}}
    cell_type = util.get_assignment_cell_type(cell)
    assert cell_type == '-'


def test_get_assignment_cell_type_given():
    """Is the cell type correct when the assignment metadata is present?"""
    cell = NotebookNode()
    cell.metadata = dict(assignment=dict(cell_type="foo"))
    cell_type = util.get_assignment_cell_type(cell)
    assert cell_type == "foo"
