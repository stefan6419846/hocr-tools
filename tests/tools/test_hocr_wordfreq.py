from __future__ import annotations

import contextlib
from io import StringIO
from unittest import mock

from hocr_tools_lib.tools import hocr_wordfreq
from tests import TestCase


class HocrWordfreqTestCase(TestCase):
    def test_word_frequencies(self) -> None:
        filename = self.get_data_file('sample.html')
        frequencies = list(
            hocr_wordfreq.word_frequencies(
                hocr_in=filename
            )
        )

        self.assertEqual(
            '23   \tthe',
            frequencies[0]
        )

    def test_case_insensitive(self) -> None:
        filename = self.get_data_file('sample.html')
        frequencies = list(
            hocr_wordfreq.word_frequencies(
                hocr_in=filename, case_insensitive=True, max_hits=30
            )
        )

        self.assertEqual(
            '24   \tthe',
            frequencies[0]
        )

    def test_main(self) -> None:
        filename = self.get_data_file('sample.html')
        stdout = StringIO()
        with mock.patch('sys.argv', ['hocr-wordfreq', str(filename)]):
            with contextlib.redirect_stdout(stdout):
                hocr_wordfreq.main()
