from __future__ import annotations

import atexit
import shutil
import sys
from contextlib import ExitStack
from pathlib import Path
from unittest import TestCase as _TestCase

if sys.version_info < (3, 10):
    import importlib_resources  # noqa: F401
else:
    import importlib.resources as importlib_resources  # noqa: F401


class TestCase(_TestCase):
    @classmethod
    def get_data_file(cls, path: str) -> str:
        file_manager = ExitStack()
        atexit.register(file_manager.close)
        reference = importlib_resources.files('tests.data') / path
        return str(file_manager.enter_context(
            importlib_resources.as_file(reference)
        ))

    @classmethod
    def get_data_content(cls, path: str) -> bytes:
        reference = importlib_resources.files('tests.data') / path
        return reference.read_bytes()

    @classmethod
    def get_data_directory(cls) -> Path:
        first_file = next(importlib_resources.files('tests.data').iterdir())
        return Path(cls.get_data_file(first_file.name)).parent

    @classmethod
    def get_data_file_copy(cls, path: str, directory: str | Path) -> Path:
        directory = Path(directory)
        source = Path(cls.get_data_file(path))
        target = directory / source.name
        shutil.copy2(src=source, dst=target)
        return target


if sys.version_info < (3, 11):  # pragma: no cover
    # Backport new functionality.
    import contextlib
    import os
    from typing import Any

    class chdir(contextlib.AbstractContextManager):  # noqa: N801
        def __init__(self, path: os.PathLike[str | bytes]) -> None:
            self.path = path
            self._old_cwd = []

        def __enter__(self) -> None:
            self._old_cwd.append(os.getcwd())
            os.chdir(self.path)

        def __exit__(self, *excinfo: Any) -> None:
            os.chdir(self._old_cwd.pop())
else:  # pragma: no cover
    from contextlib import chdir  # noqa: F401
