import json
from IPython.nbformat.current import read as read_nb
from IPython.nbformat.current import NotebookNode
from IPython.nbformat.current import new_code_cell, new_text_cell, new_notebook
from nose.tools import assert_raises
from nbgrader import AssignmentPreprocessor


class TestAssignmentPreprocessor(object):

    def setup(self):
        with open("tests/files/test.ipynb", "r") as fh:
            self.nb = read_nb(fh, 'ipynb')
        self.cells = self.nb.worksheets[0].cells
        self.preprocessor = AssignmentPreprocessor()

    @staticmethod
    def _create_code_cell():
        source = """# YOUR CODE HERE
{% if solution %}
print "hello"
{% endif %}
"""
        cell = new_code_cell(input=source, prompt_number=2, outputs=["foo"])
        return cell

    @staticmethod
    def _create_text_cell():
        source = """{% if solution %}
this is the answer!
{% else %}
YOUR ANSWER HERE
{% endif %}
"""
        cell = new_text_cell('markdown', source=source)
        return cell

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

    def test_get_toc_no_heading_cells(self):
        """Is the ToC empty if there are no heading cells?"""
        toc = self.preprocessor._get_toc([])
        assert toc == ""

    def test_get_toc(self):
        """Is the ToC correctly formatted?"""
        correct_toc = """* <a href="#foo-bar">foo bar</a>
\t* <a href="#bar">bar</a>
\t\t* <a href="#baz">baz</a>
\t\t* <a href="#quux">quux</a>
\t* <a href="#foo2">foo2</a>"""
        toc = self.preprocessor._get_toc(self.cells)
        assert toc == correct_toc

    def test_match_tests(self):
        """Are the tests matched to the correct problems?"""
        tests, rubric = self.preprocessor._match_tests(self.cells)
        assert tests == {
            "test1_for_problem1": {
                "weight": 0.5,
                "points": 1.5,
                "problem": "problem1"
            },
            "test2_for_problem1": {
                "weight": 0.5,
                "points": 1.5,
                "problem": "problem1"
            }
        }
        assert rubric == {
            "problem1": {
                "tests": ["test1_for_problem1", "test2_for_problem1"],
                "points": 3
            },
            "problem2": {
                "tests": [],
                "points": 0
            }
        }

    def test_match_tests_double_problem(self):
        """Is an error raised when a problem id is used twice?"""
        cell1 = NotebookNode()
        cell1.metadata = dict(assignment=dict(
            cell_type="grade", id="foo", points=""))
        cell2 = NotebookNode()
        cell2.metadata = dict(assignment=dict(
            cell_type="grade", id="foo", points=""))
        cells = [cell1, cell2]
        assert_raises(RuntimeError, self.preprocessor._match_tests, cells)

    def test_match_tests_no_match(self):
        """Is an error raised when an autograding cell cannot be matched?"""
        cell = NotebookNode()
        cell.metadata = dict(assignment=dict(
            cell_type="autograder"))
        cells = [cell]
        assert_raises(RuntimeError, self.preprocessor._match_tests, cells)

    def test_match_tests_double_test(self):
        """Is an error raised when a test id is used twice?"""
        cell1 = NotebookNode()
        cell1.metadata = dict(assignment=dict(
            cell_type="grade", id="foo", points=""))
        cell2 = NotebookNode()
        cell2.metadata = dict(assignment=dict(
            cell_type="autograder", id="foo_test"))
        cell3 = NotebookNode()
        cell3.metadata = dict(assignment=dict(
            cell_type="autograder", id="foo_test"))
        cells = [cell1, cell2, cell3]
        assert_raises(RuntimeError, self.preprocessor._match_tests, cells)

    def test_preprocess_nb_default_metadata(self):
        """Is the default metadata correctly set?"""
        nb, resources = self.preprocessor._preprocess_nb(self.nb, {})
        assert 'celltoolbar' not in nb.metadata
        assert nb.metadata['disable_assignment_toolbar']
        assert nb.metadata['hide_autograder_cells']

    def test_preprocess_nb_disable_toolbar(self):
        """Is the toolbar disabled?"""
        self.preprocessor.disable_toolbar = False
        nb, resources = self.preprocessor._preprocess_nb(self.nb, {})
        assert 'celltoolbar' not in nb.metadata
        assert not nb.metadata['disable_assignment_toolbar']
        assert nb.metadata['hide_autograder_cells']

    def test_preprocess_nb_hide_autograder_cells(self):
        """Are autograder cells hidden?"""
        self.preprocessor.hide_autograder_cells = False
        nb, resources = self.preprocessor._preprocess_nb(self.nb, {})
        assert 'celltoolbar' not in nb.metadata
        assert nb.metadata['disable_assignment_toolbar']
        assert not nb.metadata['hide_autograder_cells']

    def test_preprocess_code_cell_solution(self):
        """Is the solution version of a code cell correctly preprocessed?"""
        self.preprocessor.solution = True
        self.preprocessor.toc = ""
        cell = self._create_code_cell()

        self.preprocessor._create_client()
        cell, resources = self.preprocessor.preprocess_cell(cell, {}, 1)
        self.preprocessor._shutdown_client()

        output = NotebookNode()
        output.stream = "stdout"
        output.text = "hello\n"
        output.output_type = "stream"

        assert cell.input == """# YOUR CODE HERE\nprint "hello\""""
        assert cell.outputs == [output]
        # TODO: uncomment this, currently it causes the test to fail
        # because of a bug in IPython
        #assert cell.prompt_number == 1

    def test_preprocess_code_cell_release(self):
        """Is the release version of a code cell correctly preprocessed?"""
        self.preprocessor.solution = False
        self.preprocessor.toc = ""
        cell = self._create_code_cell()

        cell, resources = self.preprocessor.preprocess_cell(cell, {}, 1)
        assert cell.input == """# YOUR CODE HERE"""
        assert cell.outputs == []
        assert 'prompt_number' not in cell

    def test_preprocess_text_cell_solution(self):
        """Is the solution version of a text cell correctly preprocessed?"""
        self.preprocessor.solution = True
        self.preprocessor.toc = ""
        cell = self._create_text_cell()

        cell, resources = self.preprocessor.preprocess_cell(cell, {}, 1)
        assert cell.source == """this is the answer!"""

    def test_preprocess_text_cell_release(self):
        """Is the release version of a text cell correctly preprocessed?"""
        self.preprocessor.solution = False
        self.preprocessor.toc = ""
        cell = self._create_text_cell()

        cell, resources = self.preprocessor.preprocess_cell(cell, {}, 1)
        assert cell.source == """YOUR ANSWER HERE"""

    def test_preprocess_autograder_cells_hide(self):
        """Are autograder cells properly preprocessed and hidden?"""
        self.preprocessor.hide_autograder_cells = True
        self.preprocessor.solution = False
        cell1 = self._create_code_cell()
        cell1.metadata = dict(assignment=dict(
            cell_type="grade", id="foo", points=1))
        cell2 = self._create_code_cell()
        cell2.input = "# hello"
        cell2.metadata = dict(assignment=dict(
            cell_type="autograder", id="foo"))
        cell3 = self._create_text_cell()
        cell3.source = "goodbye"
        cell3.metadata = dict(assignment=dict(
            cell_type="autograder", id="bar"))

        nb = new_notebook(worksheets=[NotebookNode()])
        nb.worksheets[0].cells = [cell1, cell2, cell3]

        nb, resources = self.preprocessor.preprocess(nb, {})
        cell1, cell2, cell3 = nb.worksheets[0].cells
        assert cell2.input == ""
        assert cell3.source == ""

        tests = resources['tests']
        assert tests == {
            "foo": dict(weight=0.5, points=0.5, problem="foo", source="# hello"),
            "bar": dict(weight=0.5, points=0.5, problem="foo", source="goodbye")
        }

    def test_preprocess_autograder_cells_show(self):
        """Are autograder cells properly preprocessed and shown?"""
        self.preprocessor.hide_autograder_cells = False
        self.preprocessor.solution = False
        cell1 = self._create_code_cell()
        cell1.metadata = dict(assignment=dict(
            cell_type="grade", id="foo", points=1))
        cell2 = self._create_code_cell()
        cell2.input = "# hello"
        cell2.metadata = dict(assignment=dict(
            cell_type="autograder", id="foo"))
        cell3 = self._create_text_cell()
        cell3.source = "goodbye"
        cell3.metadata = dict(assignment=dict(
            cell_type="autograder", id="bar"))

        nb = new_notebook(worksheets=[NotebookNode()])
        nb.worksheets[0].cells = [cell1, cell2, cell3]

        nb, resources = self.preprocessor.preprocess(nb, {})
        cell1, cell2, cell3 = nb.worksheets[0].cells
        assert cell2.input == "# hello"
        assert cell3.source == "goodbye"

        tests = resources['tests']
        assert tests == {
            "foo": dict(weight=0.5, points=0.5, problem="foo", source="# hello"),
            "bar": dict(weight=0.5, points=0.5, problem="foo", source="goodbye")
        }

    def test_extract_outputs_release(self):
        """Are outputs excluded in release version?"""
        self.preprocessor.solution = False
        nb, resources = self.preprocessor._preprocess_nb(self.nb, {})
        self.preprocessor._extract_outputs(resources)
        assert 'outputs' not in resources

    def test_extract_outputs_solution(self):
        """Are outputs include in solution version?"""
        self.preprocessor.solution = True
        nb, resources = self.preprocessor._preprocess_nb(self.nb, {})
        self.preprocessor._extract_outputs(resources)
        assert 'outputs' in resources
        assert resources['outputs']['rubric.json'] == json.dumps(resources['rubric'])
        assert resources['outputs']['autograder_tests.json'] == json.dumps(resources['tests'])

    def test_preprocess_solution(self):
        """Does the solution preprocessor succeed?"""
        self.preprocessor.solution = True
        self.preprocessor.preprocess(self.nb, {})

    def test_preprocess_release(self):
        """Does the release preprocessor succeed?"""
        self.preprocessor.solution = False
        self.preprocessor.preprocess(self.nb, {})
