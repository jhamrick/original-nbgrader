import json

from IPython.nbconvert.preprocessors import ExecutePreprocessor
from IPython.utils.traitlets import Unicode, Int, Bool
from IPython.nbformat.current import new_code_cell, new_heading_cell, \
    new_text_cell
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
        "", config=True, info_text="Path to file containing autograding code")
    include_code = Bool(
        True, config=True,
        info_test="Whether to include autograder code in the graded notebook")
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
            "publish_data(__score__.as_dict())")
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

    def _filter_grading_cells(self, worksheet):
        """Filters out cells from the worksheet that do not have "grade"
        metadata set to True.

        """
        cells = worksheet.cells
        new_cells = []
        levels = []

        self._load_autograder(new_cells)

        for c in cells:
            heading = "/".join([x[1] for x in levels])
            if c.cell_type == 'heading':
                if "/" in c.source:
                    raise ValueError("headings should not contain slashes")
                if len(levels) == 0:
                    levels.append((c.level, c.source))
                elif c.level > levels[-1][0]:
                    self._add_grading_cell(new_cells, heading)
                    levels.append((c.level, c.source))
                else:
                    self._add_grading_cell(new_cells, heading)
                    while (len(levels) > 0) and (c.level <= levels[-1][0]):
                        levels.pop()
                    levels.append((c.level, c.source))
                new_cells.append(c)

            else:
                c.metadata['level'] = heading
                new_cells.append(c)

        self._add_autograder_code(new_cells)

        worksheet.cells = new_cells

    def _add_autograder_code(self, cells):
        if not self.autograder_code:
            return

        code = "```python\n{}\n```".format(self.autograder_code)
        cells.append(new_heading_cell(
            source="Autograder", level=self.heading_level))
        cells.append(new_text_cell(
            'markdown',
            source="The following code was used to grade this assignment:"))
        cells.append(new_text_cell('markdown', source=code))

    def _load_autograder(self, cells):
        if not self.autograder_file:
            return

        with open(self.autograder_file, "r") as fh:
            self.autograder_code = fh.read()

        ns = {}
        code = compile(self.autograder_code, "autograder", "exec")
        exec "from nbgrader import Score as score" in ns
        exec code in ns
        self.problems = ns["score"].max_grades.keys()

        cells.append(new_code_cell(input=(
            "%load_ext nbgrader\n"
            "%load_autograder {}"
        ).format(self.autograder_file)))

    def _add_grading_cell(self, cells, heading):
        if self.autograder_file and heading in self.problems:
            cells.append(new_code_cell(
                input="%grade {}".format(heading),
                metadata={"scores": True}))
