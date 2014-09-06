from collections import defaultdict
from nose.tools import make_decorator
from nose.plugins.attrib import attr
import pandas as pd


class Score(object):
    """Decorator for marking the problem an autograder test corresponds
    to, as well as the number of points that should be earned if the
    test passes.

    The `grades` and `max_grades` dictionaries should be reset (using
    `score.reset()`) before the autograding code is actually run. This
    will happen automatically if the `%%grade` magic is used.

    """

    grades = defaultdict(float)
    max_grades = defaultdict(float)

    def __init__(self, problem, points):
        self.problem = problem
        self.points = points
        self.max_grades[self.problem] += self.points

    def __call__(self, f):
        def wrapped_f(*args):
            f(*args)
            self.grades[self.problem] += self.points
        return attr(problem=self.problem)(make_decorator(f)(wrapped_f))

    @classmethod
    def reset(cls):
        cls.grades = defaultdict(float)
        cls.max_grades = defaultdict(float)

    @classmethod
    def as_dataframe(cls):
        df = pd.DataFrame({
            'score': cls.grades,
            'max_score': cls.max_grades
        }, columns=['score', 'max_score'])
        df = df.dropna()
        return df

    @classmethod
    def as_dict(cls):
        df = cls.as_dataframe()
        return df.T.to_dict()
