from .assignment_preprocessor import AssignmentPreprocessor
from .grading_preprocessor import GradingPreprocessor

__all__ = ['AssignmentPreprocessor', 'GradingPreprocessor']


from .nbgrader_extension import render_template_as


def load_ipython_extension(ipython):
    mm = ipython.magics_manager
    mm.register_function(render_template_as, 'line')
