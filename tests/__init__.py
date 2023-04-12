import shutil
import sys
from pathlib import Path
from unittest import TestCase as _TestCase

import pkg_resources


class TestCase(_TestCase):
    @classmethod
    def get_data_file(cls, path):
        return pkg_resources.resource_filename('tests', f'data/{path}')

    @classmethod
    def get_data_content(cls, path):
        return pkg_resources.resource_string('tests', f'data/{path}')

    @classmethod
    def get_data_directory(cls):
        first_file = pkg_resources.resource_listdir('tests', 'data')[0]
        return Path(cls.get_data_file(first_file)).parent

    @classmethod
    def get_data_file_copy(cls, path, directory):
        directory = Path(directory)
        source = Path(cls.get_data_file(path))
        target = directory / source.name
        shutil.copy2(src=source, dst=target)
        return target


if sys.version_info < (3, 11):  # pragma: no cover
    # Backport new functionality.
    import contextlib
    import os

    class chdir(contextlib.AbstractContextManager):  # noqa: N801
        def __init__(self, path):
            self.path = path
            self._old_cwd = []

        def __enter__(self):
            self._old_cwd.append(os.getcwd())
            os.chdir(self.path)

        def __exit__(self, *excinfo):
            os.chdir(self._old_cwd.pop())
else:  # pragma: no cover
    from contextlib import chdir  # noqa: F401
