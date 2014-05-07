import nose
import types
import os

from IPython.core.magic import Magics, magics_class, cell_magic


@magics_class
class NoseGraderMagic(Magics):

    @cell_magic
    def autograde(self, line, cell):
        cell_code = compile(cell, "<autograder>", "exec")

        ip = get_ipython()
        ip.run_code(cell_code)

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


def load_ipython_extension(ipython):
    ipython.register_magics(NoseGraderMagic)
