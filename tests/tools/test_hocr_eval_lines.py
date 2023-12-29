import contextlib
import subprocess
from io import StringIO
from unittest import mock

from hocr_tools_lib.tools import hocr_eval_lines
from tests import TestCase


class HocrEvalLinesTestCase(TestCase):
    def test_subprocess(self):
        sample_txt = self.get_data_file('sample.txt')
        sample_html = self.get_data_file('sample.html')
        subprocess.check_call(
            ['hocr-eval-lines', '-v', sample_txt, sample_html],
            stderr=subprocess.PIPE, stdout=subprocess.PIPE
        )

    def test_main(self):
        sample_txt = self.get_data_file('sample.txt')
        sample_html = self.get_data_file('sample.html')

        stdout = StringIO()
        with mock.patch(
                'sys.argv',
                ['hocr-eval-lines', '-v', sample_txt, sample_html]
        ):
            with contextlib.redirect_stdout(stdout):
                hocr_eval_lines.main()

    def test_output(self):
        tess_hocr = self.get_data_file('tess.hocr')
        sample_txt = self.get_data_file('sample.txt')

        stdout = StringIO()
        with mock.patch(
                'sys.argv',
                ['hocr-eval-lines', '-v', sample_txt, tess_hocr]
        ):
            with contextlib.redirect_stdout(stdout):
                hocr_eval_lines.main()
        stdout = stdout.getvalue()

        # Check whether detection of ocr_errors is correct.
        self.assertIn('ocr_errors 7\n', stdout)

        # Check whether detection of segmentation_errors is correct.
        self.assertIn('segmentation_errors 0', stdout)

        # CI showed output like this because of wrong 'print' syntax for 3.x
        # ('segmentation_errors', 0)
        # ('ocr_errors', 7.0)
        self.assertNotIn(
            "('segmentation_errors'", stdout,
            'Output is a string, not a stringified tuple.'
        )
