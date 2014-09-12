import json

from IPython.nbconvert.preprocessors import ExecutePreprocessor
from IPython.utils.traitlets import Unicode
from IPython.nbformat.current import new_output
from . import util


class GradingPreprocessor(ExecutePreprocessor):

    autograder_tests_file = Unicode("", config=True, info_text="Path to JSON file containing autograding code")

    def _load_autograder_tests_file(self):
        """Load the autograder tests from file"""
        if self.autograder_tests_file != "":
            with open(self.autograder_tests_file, 'r') as f:
                self.autograder_tests = json.load(f)
        else:
            self.autograder_tests = {}

    @staticmethod
    def _clear_metadata(nb):
        """Clear nbgrader metadata from the main notebook, if it exists"""
        if 'disable_assignment_toolbar' in nb.metadata:
            del nb.metadata['disable_assignment_toolbar']
        if 'hide_autograder_cells' in nb.metadata:
            del nb.metadata['hide_autograder_cells']

    def _replace_test_source(self, cell):
        """Replace the source of an autograder cell with that from the
        autograder tests file.

        """
        meta = cell.metadata['assignment']
        cell_id = meta['id']
        if cell_id in self.autograder_tests:
            test = self.autograder_tests[cell_id]
            if cell.cell_type != test['cell_type']:
                raise RuntimeError(
                    "expected cell to be of type '{}', but it is '{}'!".format(
                        test['cell_type'], cell.cell_type))

            if cell.cell_type == 'code':
                cell.input = test['source']
            else:
                cell.source = test['source']

            meta['weight'] = test['weight']
            meta['points'] = test['points']

    def _get_score(self, cell):
        """Compute the score from an autograder test, after the cell has been
        run. Returns both the score and the total possible score.

        """
        cell_id = cell.metadata['assignment']['id']
        total_score = self.autograder_tests[cell_id]['points']

        # if it is not a code cell, we can't do anything
        if cell.cell_type != 'code':
            score = float('nan')
        else:
            # if there were any errors, then the test failed
            errors = [x for x in cell.outputs if x['output_type'] == 'pyerr']
            passed = int(len(errors) == 0)
            # the score is zero if the test failed, or total_score if
            # the test passed
            score = passed * total_score

        return score, total_score

    @staticmethod
    def _add_score_output(cell, score, total_score):
        """Add a new output to the cell reporting the score earned."""
        if cell.cell_type != 'code':
            return
        output = new_output(
            'stream',
            output_text='Score: {} / {}'.format(score, total_score))
        cell.outputs.insert(0, output)

    def preprocess(self, nb, resources):
        """Grade the notebook"""
        self._load_autograder_tests_file()
        self._clear_metadata(nb)

        nb, resources = super(GradingPreprocessor, self).preprocess(
            nb, resources)

        return nb, resources

    def preprocess_cell(self, cell, resources, cell_index):
        """Execute the cell, possibly reporting a score if it is an
        autograding cell.

        """
        cell_type = util.get_assignment_cell_type(cell)

        # replace the source of tests
        if cell_type == "autograder":
            self._replace_test_source(cell)

        cell, resources = super(GradingPreprocessor, self).preprocess_cell(
            cell, resources, cell_index)

        # extract the score
        if cell_type == "autograder":
            score, total_score = self._get_score(cell)
            self._add_score_output(cell, score, total_score)

            if 'test_scores' not in resources:
                resources['test_scores'] = {}
            cell_id = cell.metadata['assignment']['id']
            resources['test_scores'][cell_id] = score

        return cell, resources
