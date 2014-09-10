import json

from IPython.nbconvert.preprocessors import ExecutePreprocessor
from IPython.utils.traitlets import Unicode
from IPython.nbformat.current import new_output


class Grader(ExecutePreprocessor):

    # configurable traitlets
    autograder_tests_file = Unicode(
        "", config=True,
        info_text="Path to JSON file containing autograding code")

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

        return nb, resources

    def preprocess_cell(self, cell, resources, cell_index):
        meta = cell.metadata.get('assignment', {})
        assignment_cell_type = meta.get('cell_type', '-')

        if assignment_cell_type == "autograder":
            test_id = meta.get('id', '')
            if test_id in self.autograder_tests:
                if cell.cell_type == 'code':
                    cell.input = self.autograder_tests[test_id]['source']
                else:
                    cell.source = self.autograder_tests[test_id]['source']

        cell, resources = super(Grader, self).preprocess_cell(
            cell, resources, cell_index)

        if assignment_cell_type == "autograder":
            if 'test_scores' not in resources:
                resources['test_scores'] = {}

            errors = [x for x in cell.outputs if x['output_type'] == 'pyerr']
            passed = int(len(errors) == 0)
            total_score = self.autograder_tests[test_id]['points']
            score = passed * total_score

            output = new_output(
                'stream',
                output_text='Score: {} / {}'.format(score, total_score))
            cell.outputs.insert(0, output)

            resources['test_scores'][meta['id']] = score

        return cell, resources
