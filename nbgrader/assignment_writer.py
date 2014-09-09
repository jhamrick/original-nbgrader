"""Based on the FilesWriter class included with IPython."""

import io
import os
import glob
import shutil

from IPython.utils.traitlets import Unicode
from IPython.utils.path import ensure_dir_exists
from IPython.utils.py3compat import unicode_type

from IPython.nbconvert.writers.base import WriterBase


class AssignmentWriter(WriterBase):

    build_directory = Unicode(
        ".", config=True, help="Directory to write output to.")

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
