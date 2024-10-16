from __future__ import annotations

import contextlib
from io import StringIO
from pathlib import Path
from unittest import mock

from hocr_tools_lib.tools import hocr_lines
from tests import TestCase


class HocrLinesTestCase(TestCase):
    def test_lines(self) -> None:
        filename = Path(self.get_data_file('tess.hocr'))
        lines = list(hocr_lines.lines(filename))

        self.assertEqual(37, len(lines))
        self.assertEqual(
            '1 Down the Rabbit-Hole',
            lines[0]
        )

    def test_main(self) -> None:
        filename = self.get_data_file('tess.hocr')
        stdout = StringIO()
        with mock.patch('sys.argv', ['hocr-lines', filename]):
            with contextlib.redirect_stdout(stdout):
                hocr_lines.main()
