import json
import numpy as np

from IPython.nbconvert.preprocessors import ExecutePreprocessor
from IPython.utils.traitlets import Unicode


class Grader(ExecutePreprocessor):

    # configurable traitlets
    autograder_tests_file = Unicode(
        "", config=True,
        info_text="Path to JSON file containing autograding code")
    scores_file = Unicode(
        "", config=True, info_text="Path to save scores")

    def preprocess(self, nb, resources):
        if len(nb.worksheets) != 1:
            raise ValueError("cannot handle more than one worksheet")

        if self.autograder_tests_file != "":
            with open(self.autograder_tests_file, 'r') as f:
                self.autograder_tests = json.load(f)
        else:
            self.autograder_tests = {}

        if 'disable_assignment_toolbar' in nb.metadata:
            del nb.metadata['disable_assignment_toolbar']
        if 'hide_autograder_cells' in nb.metadata:
            del nb.metadata['hide_autograder_cells']

        # execute all the cells
        nb, resources = super(Grader, self).preprocess(nb, resources)

        scores = {}
        for cell in nb.worksheets[0].cells:
            if 'assignment' not in cell.metadata:
                continue
            meta = cell.metadata['assignment']
            assignment_cell_type = meta['cell_type']
            if assignment_cell_type == "grade" and 'tests' in meta:
                passed = np.array(
                    [resources['tests'][x] for x in meta['tests']])
                weights = np.ones(len(passed)) / len(passed)
                total = float(meta['points'])
                scores[meta['id']] = total * np.sum(passed * weights)

        # save the scores to file
        with open(self.scores_file, 'w') as fh:
            json.dump(scores, fh)
        self.log.info("Saving scores to '{}'".format(self.scores_file))

        return nb, resources

    def preprocess_cell(self, cell, resources, cell_index):
        meta = cell.metadata.get('assignment', {})
        assignment_cell_type = meta.get('cell_type', '-')

        if assignment_cell_type == "autograder":
            test_id = meta.get('id', '')
            if test_id in self.autograder_tests:
                if cell.cell_type == 'code':
                    cell.input = self.autograder_tests[test_id]
                else:
                    cell.source = self.autograder_tests[test_id]

        cell, resources = super(Grader, self).preprocess_cell(
            cell, resources, cell_index)

        if assignment_cell_type == "autograder":
            if 'tests' not in resources:
                resources['tests'] = {}

            errors = [x for x in cell.outputs if x['output_type'] == 'pyerr']
            if len(errors) > 0:
                score = 0
            else:
                score = 1
            resources['tests'][meta['id']] = score

        return cell, resources
