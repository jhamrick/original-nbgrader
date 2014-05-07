import nose
import types
import os
import sys

from collections import defaultdict
from nose.tools import make_decorator
from IPython.core.magic import Magics, magics_class, cell_magic


class score(object):

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


@magics_class
class NoseGraderMagic(Magics):

    @cell_magic
    def autograde(self, line, cell):
        ip = get_ipython()
        ip.run_cell("from autograder import score")
        ip.run_cell(cell)

        test_module = types.ModuleType('test_module')
        test_module.__dict__.update(ip.user_ns)

        env = os.environ
        env['NOSE_TESTMATCH'] = r'(?:^|[\b_\.%s-])[Gg]rade' % os.sep
        cfg_files = nose.config.all_config_files()
        mgr = nose.plugins.manager.DefaultPluginManager()
        config = nose.config.Config(env=env, files=cfg_files, plugins=mgr)

        loader = nose.loader.TestLoader(config=config)
        tests = loader.loadTestsFromModule(test_module)
        argv = [
            "autograder",
            "--verbose",
        ]

        nose.core.TestProgram(
            argv=argv, suite=tests, exit=False, config=config)

        sys.stderr.flush()
        sys.stdout.flush()
        grades = test_module.__dict__['score'].grades
        max_grades = test_module.__dict__['score'].max_grades

        for problem in max_grades:
            print "{0} : {1:.1f} / {2:.1f} points".format(
                problem, grades[problem], max_grades[problem])


def load_ipython_extension(ipython):
    ipython.register_magics(NoseGraderMagic)
