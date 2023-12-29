import contextlib
import subprocess
from io import StringIO
from unittest import mock

from hocr_tools_lib.tools import hocr_check
from tests import TestCase


class HocrCheckTestCase(TestCase):
    def test_from_filename(self):
        filename = self.get_data_file('sample.html')
        subprocess.check_call(
            ['hocr-check', filename], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stderr = StringIO()
        with mock.patch('sys.argv', ['hocr-check', filename]):
            with contextlib.redirect_stderr(stderr):
                hocr_check.main()

    def test_from_stdin(self):
        filename = self.get_data_file('sample.html')
        subprocess.check_call(
            [f'cat {filename} | hocr-check'], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, shell=True
        )

    def test_valid_examples(self):
        directory = self.get_data_directory() / 'hocr_check'
        for path in directory.rglob('ok-*html'):
            with self.subTest(path=path):
                stderr = StringIO()
                with contextlib.redirect_stderr(stderr):
                    hocr_check.Checker(hocr_file=path).check()
                stderr = stderr.getvalue()
                self.assertNotIn('not ok', stderr)

    def test_invalid_examples(self):
        directory = self.get_data_directory() / 'hocr_check'
        for path in directory.rglob('notok-*html'):
            with self.subTest(path=path):
                stderr = StringIO()
                with contextlib.redirect_stderr(stderr):
                    hocr_check.Checker(hocr_file=path).check()
                stderr = stderr.getvalue()
                self.assertIn('not ok', stderr)
