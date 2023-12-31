from __future__ import annotations

import contextlib
import subprocess
from io import StringIO
from tempfile import TemporaryDirectory
from unittest import mock

from hocr_tools_lib.tools import hocr_cut
from tests import TestCase


class HocrCutTestCase(TestCase):
    def test_subprocess(self) -> None:
        with TemporaryDirectory() as directory:
            filename = self.get_data_file_copy(
                'litver.html', directory=directory
            )
            self.get_data_file_copy('litver.png', directory=directory)
            subprocess.check_call(
                ['hocr-cut', filename], stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

    def test_main(self) -> None:
        with TemporaryDirectory() as directory:
            filename = self.get_data_file_copy(
                'litver.html', directory=directory
            )
            self.get_data_file_copy('litver.png', directory=directory)

            stdout = StringIO()
            with mock.patch('sys.argv', ['hocr-cut', str(filename)]):
                with contextlib.redirect_stdout(stdout):
                    hocr_cut.main()

    def test_generated_files(self) -> None:
        with TemporaryDirectory() as temp_directory:
            filename = self.get_data_file_copy(
                'litver.html', directory=temp_directory
            )
            self.get_data_file_copy('litver.png', directory=temp_directory)
            directory = filename.parent

            stdout = StringIO()
            with contextlib.redirect_stdout(stdout):
                hocr_cut.cut(filename, debug=True)

            self.assertNotEqual(
                b'',
                (directory / 'litver.left.png').read_bytes()
            )
            self.assertNotEqual(
                b'',
                (directory / 'litver.right.png').read_bytes()
            )
            self.assertNotEqual(
                b'',
                (directory / 'litver.cut.png').read_bytes()
            )
