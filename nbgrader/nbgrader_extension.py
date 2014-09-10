from __future__ import print_function

import jinja2
import sys

from IPython.core.inputtransformer import InputTransformer


class SolutionInputTransformer(InputTransformer):
    """IPython input transformer that renders jinja templates in cells,
    allowing them to be run while the instructor is developing the
    assignment.

    Original version written by minrk:
    http://nbviewer.ipython.org/gist/minrk/c2b26ee47b7caaaa0c74

    """

    def __init__(self, solution, *args, **kwargs):
        super(SolutionInputTransformer, self).__init__(*args, **kwargs)

        self.solution = solution
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
            return template.render(solution=self.solution)
        except Exception as e:
            print("Failed to render jinja template: %s" % e, file=sys.stderr)
            return text


def render_template_as(line):
    if line.strip() not in ("solution", "release"):
        raise ValueError("invalid mode: {}".format(line.strip()))
    solution = line.strip() == "solution"

    ip = get_ipython()
    transforms = ip.input_transformer_manager.python_line_transforms
    transforms.append(SolutionInputTransformer(solution))
