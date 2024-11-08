from __future__ import annotations

import contextlib
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

import requests
from PIL import Image
from pypdf import PdfReader
from pypdf.generic import RectangleObject

from hocr_tools_lib.tools import hocr_pdf
from tests import TestCase


class HocrPdfTestCase(TestCase):
    BASE_URL = 'https://digi.bib.uni-mannheim.de/fileadmin/digi/445442158'
    WORK = '445442158_0126'

    def _download_files(self, directory: Path, skip_hocr: bool = False) -> None:
        hocr_file = directory / f'{self.WORK}.hocr'
        jpg_file = directory / f'{self.WORK}.jpg'

        session = requests.Session()
        self.addCleanup(session.close)

        if not skip_hocr:
            response = session.get(f'{self.BASE_URL}/tess/{self.WORK}.hocr')
            self.assertEqual(200, response.status_code)
            hocr_file.write_bytes(response.content)
            self.assertLess(1, hocr_file.stat().st_size)

        response = session.get(f'{self.BASE_URL}/max/{self.WORK}.jpg')
        self.assertEqual(200, response.status_code)
        jpg_file.write_bytes(response.content)
        self.assertLess(1, jpg_file.stat().st_size)

    def _check_content(self, pdf_path: Path, key: str) -> None:
        self.assertLess(1, pdf_path.stat().st_size)

        with PdfReader(pdf_path) as reader:
            self.assertEqual(1, len(reader.pages))
            self.assertIn(key, reader.pages[0].extract_text())

    def test_export_pdf(self) -> None:
        with TemporaryDirectory() as temp_directory:
            directory = Path(temp_directory)
            self._download_files(directory)

            pdf_path = directory / f'{self.WORK}.pdf'
            stdout = StringIO()
            with contextlib.redirect_stdout(stdout):
                hocr_pdf.export_pdf(directory=str(directory))
            pdf_path.write_text(stdout.getvalue())
            self._check_content(pdf_path, 'tribunali')

            pdf_path = directory / f'{self.WORK}-saved.pdf'
            hocr_pdf.export_pdf(directory=str(directory), savefile=str(pdf_path))
            self._check_content(pdf_path, 'tribunali')

    def test_export_pdf__kraken(self) -> None:
        with TemporaryDirectory() as temp_directory:
            directory = Path(temp_directory)
            self._download_files(directory, skip_hocr=True)

            hocr_source_path = self.get_data_file('hocr_pdf/kraken.hocr')
            hocr_path = directory / f'{self.WORK}.hocr'
            hocr_path.write_bytes(Path(hocr_source_path).read_bytes())

            pdf_path = directory / f'{self.WORK}-saved.pdf'
            hocr_pdf.export_pdf(directory=str(directory), savefile=str(pdf_path))
            self._check_content(pdf_path, 'Hello World')

    def test_export_pdf__page_size(self) -> None:
        with TemporaryDirectory() as temp_directory:
            directory = Path(temp_directory)
            self._download_files(directory)

            image_path = directory / f'{self.WORK}.jpg'
            image: Image.Image = Image.new(mode='RGB', size=(2458, 3150), color=(0, 0, 0))
            image.save(image_path)

            pdf_path = directory / f'{self.WORK}-saved.pdf'
            hocr_pdf.export_pdf(directory=str(directory), savefile=str(pdf_path))
            self._check_content(pdf_path, 'tribunali')

            with PdfReader(pdf_path) as reader:
                size: RectangleObject = reader.pages[0].mediabox
                self.assertEqual((589, 756), size.upper_right)

    def test_main(self) -> None:
        with TemporaryDirectory() as temp_directory:
            directory = Path(temp_directory)
            self._download_files(directory)

            stdout = StringIO()
            with mock.patch('sys.argv', ['hocr-pdf', str(directory)]):
                with contextlib.redirect_stdout(stdout):
                    hocr_pdf.main()
