import json
import math
from IPython.nbformat.current import read as read_nb
from IPython.nbformat.current import NotebookNode
from IPython.nbformat.current import new_code_cell, new_text_cell, new_notebook
from nose.tools import assert_raises
from nbgrader import GradingPreprocessor


class TestAssignmentPreprocessor(object):

    def setup(self):
        with open("tests/files/test.ipynb", "r") as fh:
            self.nb = read_nb(fh, 'ipynb')
        self.cells = self.nb.worksheets[0].cells
        self.preprocessor = GradingPreprocessor()
        self.preprocessor.autograder_tests_file = "tests/files/autograder_tests.json"

    def test_load_autograder_tests_file_none(self):
        """Is an empty dict returned when there is no test file specified?"""
        self.preprocessor.autograder_tests_file = ""
        self.preprocessor._load_autograder_tests_file()
        assert self.preprocessor.autograder_tests == {}

    def test_load_autograder_tests_file_invalid(self):
        """Is an error raised when there is the test file is missing?"""
        self.preprocessor.autograder_tests_file = "foo.json"
        assert_raises(IOError, self.preprocessor._load_autograder_tests_file)

    def test_load_autograder_tests_file_ok(self):
        """Are the autograder tests correctly loaded?"""
        self.preprocessor._load_autograder_tests_file()
        with open("tests/files/autograder_tests.json", "r") as fh:
            tests = json.load(fh)
        assert self.preprocessor.autograder_tests == tests

    def test_clear_metadata(self):
        """Is the metadata properly cleared?"""
        nb = new_notebook()
        nb.metadata['disable_assignment_toolbar'] = True
        nb.metadata['hide_autograder_cells'] = True
        self.preprocessor._clear_metadata(nb)
        assert 'disable_assignment_toolbar' not in nb.metadata
        assert 'hide_autograder_cells' not in nb.metadata

    def test_replace_test_source_code(self):
        """Is the code source properly replaced?"""
        cell = new_code_cell("\n", metadata=dict(
            assignment=dict(id="test1_for_problem1")))
        self.preprocessor._load_autograder_tests_file()
        self.preprocessor._replace_test_source(cell)
        assert cell.input == "# blah blah blah"
        assert cell.metadata['assignment']['weight'] == 0.3333333333333333
        assert cell.metadata['assignment']['points'] == 1

    def test_replace_test_source_text(self):
        """Is the text source properly replaced?"""
        cell = new_text_cell("markdown", metadata=dict(
            assignment=dict(id="test2_for_problem1")))
        self.preprocessor._load_autograder_tests_file()
        self.preprocessor._replace_test_source(cell)
        assert cell.source == "# blah blah blah blah"
        assert cell.metadata['assignment']['weight'] == 0.6666666666666666
        assert cell.metadata['assignment']['points'] == 2

    def test_replace_test_source_bad_cell_type(self):
        """Is an error raised if the cell type has changed?"""
        cell = new_text_cell("markdown", metadata=dict(
            assignment=dict(id="test1_for_problem1")))
        self.preprocessor._load_autograder_tests_file()
        assert_raises(
            RuntimeError, self.preprocessor._replace_test_source, cell)

    def test_get_score_error(self):
        """Is the score zero when there was an error?"""
        cell = new_code_cell("\n", metadata=dict(
            assignment=dict(id="test1_for_problem1")))
        cell.outputs = [NotebookNode()]
        cell.outputs[0]['output_type'] = 'pyerr'
        self.preprocessor._load_autograder_tests_file()
        score, total_score = self.preprocessor._get_score(cell)
        assert score == 0
        assert total_score == 1

    def test_get_score_ok(self):
        """Is the score zero when there was no error?"""
        cell = new_code_cell("\n", metadata=dict(
            assignment=dict(id="test1_for_problem1")))
        cell.outputs = []
        self.preprocessor._load_autograder_tests_file()
        score, total_score = self.preprocessor._get_score(cell)
        assert score == 1
        assert total_score == 1

    def test_get_score_nan(self):
        """Is the score nan when the cell is text?"""
        cell = new_text_cell("markdown", metadata=dict(
            assignment=dict(id="test1_for_problem1")))
        cell.outputs = []
        self.preprocessor._load_autograder_tests_file()
        score, total_score = self.preprocessor._get_score(cell)
        assert math.isnan(score)
        assert total_score == 1

    def test_add_score_output(self):
        """Is the score properly formatted and added to the cell outputs?"""
        cell = NotebookNode()
        cell.cell_type = 'code'
        cell.outputs = []
        self.preprocessor._add_score_output(cell, 10, 15)
        output = cell.outputs[0]
        assert output.stream == "stdout"
        assert output.output_type == "stream"
        assert output.text == "Score: 10 / 15"

    def test_add_score_output_text(self):
        """Is the score properly handled when the cell is a markdown cell?"""
        cell = NotebookNode()
        cell.cell_type = 'markdown'
        cell.outputs = []
        self.preprocessor._add_score_output(cell, 10, 15)
        assert cell['outputs'] == []

    def test_preprocess(self):
        """Does the preprocessor run without failing?"""
        self.preprocessor.preprocess(self.nb, {})
