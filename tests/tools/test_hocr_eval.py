from __future__ import annotations

import contextlib
import subprocess
from io import StringIO
from unittest import mock

from hocr_tools_lib.tools import hocr_eval
from tests import TestCase


class HocrEvalTestCase(TestCase):
    def test_with_self(self) -> None:
        filename = self.get_data_file('sample.html')
        subprocess.check_call(
            ['hocr-eval', filename, filename], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_verbose_and_debug_mode(self) -> None:
        tess_hocr = self.get_data_file('tess.hocr')
        sample_html = self.get_data_file('sample.html')
        subprocess.check_call(
            ['hocr-eval', '-d', '-v', tess_hocr, sample_html],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )

    def test_main(self) -> None:
        tess_hocr = self.get_data_file('tess.hocr')
        sample_html = self.get_data_file('sample.html')

        stdout = StringIO()
        with mock.patch('sys.argv', ['hocr-eval', tess_hocr, sample_html]):
            with contextlib.redirect_stdout(stdout):
                hocr_eval.main()

        stdout = StringIO()
        with mock.patch('sys.argv', ['hocr-eval', sample_html, sample_html]):
            with contextlib.redirect_stdout(stdout):
                hocr_eval.main()
