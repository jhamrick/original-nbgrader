from .assignment_preprocessor import AssignmentPreprocessor
from .assignment_writer import AssignmentWriter
from .grading_preprocessor import Grader
from .score import Score

__all__ = ['AssignmentPreprocessor', 'AssignmentWriter', 'Grader', 'Score']


from .nbgrader_extension import NoseGraderMagic, run_solutions


def load_ipython_extension(ipython):
    ipython.register_magics(NoseGraderMagic)
    mm = ipython.magics_manager
    mm.register_function(run_solutions, 'line')
