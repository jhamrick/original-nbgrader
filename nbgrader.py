import json

from IPython.nbconvert.preprocessors import ExecutePreprocessor
from IPython.utils.traitlets import Unicode, Int
from IPython.nbformat.current import new_heading_cell, new_code_cell
from IPython.kernel.zmq import serialize

try:
    from queue import Empty  # Py 3
except ImportError:
    from Queue import Empty  # Py 2


class Grader(ExecutePreprocessor):

    # configurable traitlets
    assignment = Unicode(
        "", config=True, info_text="Assignment name")
    autograder_file = Unicode(
        "", config=True, info_text="Path to autograding code")
    scores_file = Unicode(
        "", config=True, info_text="Path to save scores")
    heading_level = Int(
        1, config=True, info_text="Level for heading cells")

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

        # save the scores to file
        if 'scores' in resources:
            scores = resources['scores']
            with open(self.scores_file, 'w') as fh:
                json.dump(scores, fh)
            self.log.info("Saving scores to '{}'".format(self.scores_file))

        return nb, resources

    def preprocess_cell(self, cell, resources, cell_index):
        cell, resources = super(Grader, self).preprocess_cell(
            cell, resources, cell_index)

        # if the cell is marked as returning scores, then extract the
        # scores from it, and remove the metadata flag
        if self.scores_file and cell.metadata.get('scores', False):
            scores = self._get_scores()
            if 'scores' not in resources:
                resources['scores'] = []
            resources['scores'].extend(scores)
            del cell.metadata['scores']

        return cell, resources

    def _get_scores(self):
        """Publish score data from the notebook as a dictionary."""

        # send the "publish data" message, which will send the
        # (serialized) raw data
        self.shell.execute(
            "from IPython.kernel.zmq.datapub import publish_data\n"
            "publish_data(score.as_dict())")
        self.shell.get_msg(timeout=20)

        # read the message with the data, and unserialize it
        score_data = []
        while True:
            try:
                msg = self.iopub.get_msg(timeout=0.2)
            except Empty:
                break

            if msg['msg_type'] == 'data_message':
                data, remainder = serialize.unserialize_object(msg['buffers'])
                score_data.append(data)

        return score_data

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
        if not self.autograder_file:
            return

        # load the code and prepend the cell magic
        with open(self.autograder_file, 'r') as fh:
            autograder_code = "%%autograde\n\n"
            autograder_code += fh.read().strip()

        # create the new cells
        cells.append(new_heading_cell(
            source="Autograder", level=self.heading_level))
        cells.append(new_code_cell(input="%load_ext autograder"))
        if self.scores_file:
            cells.append(new_code_cell(
                input=autograder_code, metadata={"scores": True}))
        else:
            cells.append(new_code_cell(input=autograder_code))
