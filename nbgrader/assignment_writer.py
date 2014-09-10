"""Based on the FilesWriter class included with IPython."""

import io
import os
import glob
import shutil
import json

from IPython.utils.traitlets import Unicode, Bool
from IPython.utils.path import ensure_dir_exists
from IPython.utils.py3compat import unicode_type

from IPython.nbconvert.writers.base import WriterBase


class AssignmentWriter(WriterBase):

    build_directory = Unicode(
        ".", config=True, help="Directory to write output to.")
    save_rubric = Bool(
        False, config=True, help="Whether to save out rubric file")
    rubric_file = Unicode(
        "rubric", config=True, help="Filename to write JSON rubric to")
    save_autograder_tests = Bool(
        False, config=True, help="Whether to save out autograder tests")
    autograder_test_file = Unicode(
        "autograder_tests", config=True,
        help="Filename to write JSON autograder tests to")

    # Make sure that the output directory exists.
    def _build_directory_changed(self, name, old, new):
        if new:
            ensure_dir_exists(new)

    def __init__(self, **kw):
        super(AssignmentWriter, self).__init__(**kw)
        self._build_directory_changed(
            'build_directory', self.build_directory, self.build_directory)

    def _makedir(self, path):
        """Make a directory if it doesn't already exist"""
        if path:
            self.log.info("Making directory %s", path)
            ensure_dir_exists(path)

    def write(self, output, resources, notebook_name=None, **kw):
        """Consume and write Jinja output to the file system.  Output
        directory is set via the 'build_directory' variable of this
        instance (a configurable).

        See base for more...

        """

        # Verify that a notebook name is provided.
        if notebook_name is None:
            raise TypeError('notebook_name')

        # Pull the extension and subdir from the resources dict.
        output_extension = resources.get('output_extension', None)

        # Save out the rubric, if requested
        if self.save_rubric:
            rubric = resources.get('rubric', {})
            rubric_file = self.rubric_file + ".json"
            if self.build_directory:
                dest = os.path.join(self.build_directory, rubric_file)
            else:
                dest = rubric_file

            with io.open(dest, 'wb') as f:
                self.log.info("Writing %s", dest)
                json.dump(rubric, f, indent=1, sort_keys=True)

        # Save out the autograder tests, if requested
        if self.save_autograder_tests:
            tests = resources.get('tests', {})
            test_file = self.autograder_test_file + ".json"
            if self.build_directory:
                dest = os.path.join(self.build_directory, test_file)
            else:
                dest = test_file

            with io.open(dest, 'wb') as f:
                self.log.info("Writing %s", dest)
                json.dump(tests, f, indent=1, sort_keys=True)

        # Copy referenced files to output directory
        if self.build_directory:
            for filename in self.files:

                # Copy files that match search pattern
                for matching_filename in glob.glob(filename):

                    # Make sure folder exists.
                    dest = os.path.join(
                        self.build_directory, matching_filename)
                    path = os.path.dirname(dest)
                    self._makedir(path)

                    # Copy if destination is different.
                    if not os.path.normpath(dest) == os.path.normpath(matching_filename):
                        self.log.info("Copying %s -> %s",
                                      matching_filename, dest)
                        shutil.copy(matching_filename, dest)

        # Determine where to write conversion results.
        if output_extension is not None:
            dest = notebook_name + '.' + output_extension
        else:
            dest = notebook_name
        if self.build_directory:
            dest = os.path.join(self.build_directory, dest)

        # Write conversion results.
        self.log.info("Writing %i bytes to %s", len(output), dest)
        if isinstance(output, unicode_type):
            with io.open(dest, 'w', encoding='utf-8') as f:
                f.write(output)
        else:
            with io.open(dest, 'wb') as f:
                f.write(output)

        return dest
