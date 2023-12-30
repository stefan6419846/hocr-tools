from __future__ import annotations

import contextlib
import subprocess
from io import StringIO
from unittest import mock

from hocr_tools_lib.tools import hocr_combine
from tests import TestCase


class HocrCombineTestCase(TestCase):
    def test_subprocess(self) -> None:
        filename = self.get_data_file('sample.html')
        subprocess.check_call(
            ['hocr-combine', filename, filename], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_main(self) -> None:
        filename = self.get_data_file('sample.html')
        stdout = StringIO()
        with mock.patch('sys.argv', ['hocr-combine', filename, filename]):
            with contextlib.redirect_stdout(stdout):
                hocr_combine.main()

    def test_ocr_line_count(self) -> None:
        def count(content_):
            return content_.count('class="ocr_line"') + \
                content_.count("class='ocr_line'")

        filename = self.get_data_file('sample.html')
        content = self.get_data_content('sample.html')
        original_count = count(content.decode('UTF-8'))

        merged = hocr_combine.combine([filename, filename])
        merged_count = count(merged)

        # Check whether number ocr_lines in self-combined result is doubled.
        self.assertEqual(original_count * 2, merged_count)
