from .assignment_preprocessor import ReleasePreprocessor
from .grading_preprocessor import Grader
from .score import Score

__all__ = ['ReleasePreprocessor', 'Grader', 'Score']


from .nbgrader_extension import NoseGraderMagic, run_solutions


def load_ipython_extension(ipython):
    ipython.register_magics(NoseGraderMagic)
    mm = ipython.magics_manager
    mm.register_function(run_solutions, 'line')
