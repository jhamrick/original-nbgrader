from IPython.nbconvert.preprocessors import ExecutePreprocessor
from IPython.utils.traitlets import Unicode, Int
from IPython.nbformat.current import new_heading_cell, new_code_cell


class Grader(ExecutePreprocessor):

    # configurable traitlets
    assignment = Unicode("", config=True, info_text="Assignment name")
    autograder = Unicode("", config=True, info_text="Path to autograding code")
    heading_level = Int(1, config=True, info_text="Level for heading cells")

    def preprocess(self, nb, resources):
        if len(nb.worksheets) != 1:
            raise ValueError("cannot handle more than one worksheet")

        # extract only cells that have grade=True metadata
        self._filter_grading_cells(nb.worksheets[0])

        # set notebook name, and clear other metadata
        nb.metadata = {"name": self.assignment}

        # load autograder
        self._load_autograder(nb.worksheets[0].cells)

        # execute all the cells
        nb, resources = super(Grader, self).preprocess(nb, resources)

        return nb, resources

    @staticmethod
    def _filter_grading_cells(worksheet):
        """Filters out cells from the worksheet that do not have "grade"
        metadata set to True.

        """
        cells = worksheet.cells
        new_cells = [c for c in cells if c.metadata.get('grade', False)]
        worksheet.cells = new_cells

    def _load_autograder(self, cells):
        """Loads grading code from file, according to the c.Grader.autograder
        traitlet, and then creates several new cells:

        1. A heading cell called "Autograder". Will be created at the
           level specified by c.Grader.heading_level
        2. A code cell to load the autograder extension.
        3. A code cell containing the loaded grading code, prepended
           with the `%%autograde` magic.

        These cells are appended to the given list of cells.

        """

        # don't do anything if there is no grading code
        if not self.autograder:
            return

        # load the code and prepend the cell magic
        with open(self.autograder, 'r') as fh:
            autograder_code = "%%autograde\n\n"
            autograder_code += fh.read().strip()

        # create the new cells
        cells.append(new_heading_cell(
            source="Autograder", level=self.heading_level))
        cells.append(new_code_cell(input="%load_ext autograder"))
        cells.append(new_code_cell(input=autograder_code))
