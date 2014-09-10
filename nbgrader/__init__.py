from .assignment_preprocessor import AssignmentPreprocessor
from .assignment_writer import AssignmentWriter
from .grading_preprocessor import Grader
from .score import Score

__all__ = ['AssignmentPreprocessor', 'AssignmentWriter', 'Grader', 'Score']


from .nbgrader_extension import render_template_as


def load_ipython_extension(ipython):
    mm = ipython.magics_manager
    mm.register_function(render_template_as, 'line')
