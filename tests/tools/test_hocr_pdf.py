from __future__ import annotations

import contextlib
import shutil
import subprocess
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

import requests
from hocr_tools_lib.tools import hocr_pdf
from tests import TestCase


class HocrPdfTestCase(TestCase):
    BASE_URL = 'https://digi.bib.uni-mannheim.de/fileadmin/digi/445442158'
    WORK = '445442158_0126'

    def _download_files(self, directory: Path) -> None:
        hocr_file = directory / f'{self.WORK}.hocr'
        jpg_file = directory / f'{self.WORK}.jpg'

        session = requests.Session()
        self.addCleanup(session.close)

        response = session.get(f'{self.BASE_URL}/tess/{self.WORK}.hocr')
        self.assertEqual(200, response.status_code)
        hocr_file.write_bytes(response.content)
        self.assertLess(1, hocr_file.stat().st_size)

        response = session.get(f'{self.BASE_URL}/max/{self.WORK}.jpg')
        self.assertEqual(200, response.status_code)
        jpg_file.write_bytes(response.content)
        self.assertLess(1, jpg_file.stat().st_size)

    def _check_content(self, pdf_path: Path) -> None:
        self.assertLess(1, pdf_path.stat().st_size)
        subprocess.check_call(
            ['pdfgrep', 'tribunali', str(pdf_path)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    def test_export_pdf(self) -> None:
        if shutil.which('pdfgrep') is None:
            self.skipTest(
                'Test requires `pdfgrep` installed.'
            )  # pragma: no cover

        with TemporaryDirectory() as temp_directory:
            directory = Path(temp_directory)
            self._download_files(directory)

            pdf_path = directory / f'{self.WORK}.pdf'
            stdout = StringIO()
            with contextlib.redirect_stdout(stdout):
                hocr_pdf.export_pdf(directory=str(directory))
            pdf_path.write_text(stdout.getvalue())
            self._check_content(pdf_path)

            pdf_path = directory / f'{self.WORK}-saved.pdf'
            hocr_pdf.export_pdf(directory=str(directory), savefile=str(pdf_path))
            self._check_content(pdf_path)

    def test_main(self) -> None:
        with TemporaryDirectory() as temp_directory:
            directory = Path(temp_directory)
            self._download_files(directory)

            stdout = StringIO()
            with mock.patch('sys.argv', ['hocr-pdf', str(directory)]):
                with contextlib.redirect_stdout(stdout):
                    hocr_pdf.main()
