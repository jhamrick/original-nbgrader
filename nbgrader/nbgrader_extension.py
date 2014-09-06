from __future__ import print_function

import nose
import types
import os
import jinja2
import sys

from nose.plugins.attrib import AttributeSelector

from IPython.core.magic import Magics, magics_class
from IPython.core.magic import line_magic, line_cell_magic
from IPython.core.inputtransformer import InputTransformer


@magics_class
class NoseGraderMagic(Magics):

    @line_cell_magic
    def grade(self, line, cell=None):
        ip = get_ipython()
        if cell is not None:
            ip.run_cell("__score__.reset(); score = __score__")
            ip.run_cell(cell)
        else:
            ip.run_cell("__score__.reset(); score = __score__")
            ip.run_cell(self.autograder_code)

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
        plug = AttributeSelector()
        plug.attribs = [[("problem", line)]]
        plug.enabled = True
        mgr = nose.plugins.manager.DefaultPluginManager(
            plugins=[plug])

        # create the nose configuration object, and load the tests
        config = nose.config.Config(env=env, files=cfg_files, plugins=mgr)
        loader = nose.loader.TestLoader(config=config)
        tests = loader.loadTestsFromModule(test_module)

        # run the tests
        nose.core.TestProgram(
            argv=["autograder", "--verbose"],
            suite=tests, exit=False, config=config)

        # create a pandas dataframe of the scores, and return it
        if '__score__' in test_module.__dict__:
            return test_module.__dict__['__score__'].as_dataframe()

    @line_magic
    def load_autograder(self, line):
        ip = get_ipython()
        ip.run_cell("from nbgrader import Score as __score__")
        with open(line, 'r') as fh:
            self.autograder_code = fh.read()


class SolutionInputTransformer(InputTransformer):
    """IPython input transformer that renders jinja templates in cells,
    allowing them to be run while the instructor is developing the
    assignment.

    Original version written by minrk:
    http://nbviewer.ipython.org/gist/minrk/c2b26ee47b7caaaa0c74

    """

    def __init__(self, *args, **kwargs):
        super(SolutionInputTransformer, self).__init__(*args, **kwargs)

        self.env = jinja2.Environment()
        self._lines = []

    def push(self, line):
        self._lines.append(line)
        return None

    def reset(self):
        text = u'\n'.join(self._lines)
        self._lines = []
        template = self.env.from_string(text)
        try:
            return template.render(solution=True)
        except Exception as e:
            print("Failed to render jinja template: %s" % e, file=sys.stderr)
            return text


def run_solutions(line):
    ip = get_ipython()
    ip.input_transformer_manager.physical_line_transforms.insert(
        0, SolutionInputTransformer()
    )
