import nose
import types
import os
import pandas as pd

from collections import defaultdict
from nose.tools import make_decorator
from IPython.core.magic import Magics, magics_class, cell_magic


class score(object):
    """Decorator for marking the problem an autograder test corresponds
    to, as well as the number of points that should be earned if the
    test passes.

    The `grades` and `max_grades` dictionaries should be reset (using
    `score.reset()`) before the autograding code is actually run. This
    will happen automatically if the `%%autograde` magic is used.

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
        return make_decorator(f)(wrapped_f)

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
        df.fillna(0, inplace=True)
        return df

    @classmethod
    def as_dict(cls):
        df = cls.as_dataframe()
        return df.T.to_dict()


@magics_class
class NoseGraderMagic(Magics):

    @cell_magic
    def autograde(self, line, cell):
        # get the ipython user session, import the score decorator,
        # and then run the autograding code (which will load the tests
        # into the namespace)
        ip = get_ipython()
        ip.run_cell("from autograder import score; score.reset()")
        ip.run_cell(cell)

        # create the test module for nose
        test_module = types.ModuleType('test_module')
        test_module.__dict__.update(ip.user_ns)

        # change the test name template to use "grade" instead of
        # "test" (which is the default)
        env = os.environ
        env['NOSE_TESTMATCH'] = r'(?:^|[\b_\.%s-])[Gg]rade' % os.sep

        # load user config files
        cfg_files = nose.config.all_config_files()

        # create a plugin manager
        mgr = nose.plugins.manager.DefaultPluginManager()

        # create the nose configuration object, and load the tests
        config = nose.config.Config(env=env, files=cfg_files, plugins=mgr)
        loader = nose.loader.TestLoader(config=config)
        tests = loader.loadTestsFromModule(test_module)

        # run the tests
        nose.core.TestProgram(
            argv=["autograder", "--verbose"],
            suite=tests, exit=False, config=config)

        # create a pandas dataframe of the scores, and return it
        return test_module.__dict__['score'].as_dataframe()


def load_ipython_extension(ipython):
    ipython.register_magics(NoseGraderMagic)
