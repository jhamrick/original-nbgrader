from IPython.nbconvert.preprocessors import ExecutePreprocessor
from IPython.utils.traitlets import Unicode, Int
from IPython.nbformat.current import new_heading_cell, new_code_cell


class Grader(ExecutePreprocessor):

    assignment = Unicode("", config=True, info_text="Assignment name")
    autograder = Unicode("", config=True, info_text="Path to autograding code")
    heading_level = Int(1, config=True, info_text="Level for heading cells")

    @staticmethod
    def _filter_grading_cells(worksheet):
        cells = worksheet.cells
        new_cells = [c for c in cells if c.metadata.get('grade', False)]
        worksheet.cells = new_cells

    def _load_autograder(self, cells):
        with open(self.autograder, 'r') as fh:
            autograder_code = "%%autograde\n\n"
            autograder_code += fh.read().strip()

        cells.append(new_heading_cell(
            source="Autograder", level=self.heading_level))
        cells.append(new_code_cell(input="%load_ext autograder"))
        cells.append(new_code_cell(input=autograder_code))

        # cells.append(new_heading_cell(
        #     source="Coding scores", level=2))
        # cells.append(new_code_cell(
        #     input="grades = dict(grades)\ngrades"))
        # cells.append(new_code_cell(
        #     input="import json; json.dumps(grades)"))

    def preprocess(self, nb, resources):
        if len(nb.worksheets) != 1:
            raise ValueError("cannot handle more than one worksheet")

        # extract only cells that have grade=True metadata
        self._filter_grading_cells(nb.worksheets[0])

        # set notebook name, and clear other metadata
        nb.metadata = {"name": self.assignment}

        # load autograder
        if self.autograder:
            self._load_autograder(nb.worksheets[0].cells)

        # execute all the cells
        nb, resources = super(Grader, self).preprocess(nb, resources)

        return nb, resources
