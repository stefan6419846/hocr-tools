import contextlib
import subprocess
from io import StringIO
from unittest import mock

from hocr_tools.tools import hocr_eval_geom
from tests import TestCase


class HocrEvalGeomTestCase(TestCase):
    def test_with_self(self):
        filename = self.get_data_file('sample.html')
        stdout = subprocess.check_output(
            ['hocr-eval-geom', filename, filename],
            stderr=subprocess.PIPE
        )
        self.assertRegex(stdout, br'\(0, 0, 0.0, ')

    def test_with_options(self):
        tess_hocr = self.get_data_file('tess.hocr')
        sample_html = self.get_data_file('sample.html')
        subprocess.check_call(
            [
                'hocr-eval-geom', '-e', 'ocr_line', '-o', '0.05',
                '-c', '0.88', tess_hocr, sample_html
            ],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )

    def test_main(self):
        tess_hocr = self.get_data_file('tess.hocr')
        sample_html = self.get_data_file('sample.html')

        stdout = StringIO()
        with mock.patch(
                'sys.argv',
                ['hocr-eval-geom', tess_hocr, sample_html]
        ):
            with contextlib.redirect_stdout(stdout):
                hocr_eval_geom.main()

        stdout = StringIO()
        with mock.patch(
                'sys.argv',
                ['hocr-eval-geom', sample_html, sample_html]
        ):
            with contextlib.redirect_stdout(stdout):
                hocr_eval_geom.main()
