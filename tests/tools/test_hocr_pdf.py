from __future__ import annotations

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
    BASE_URL = "https://digi.bib.uni-mannheim.de/fileadmin/digi/445442158"
    WORK = "445442158_0126"

    hocr_data = b""
    jpg_data = b""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        with requests.Session() as session:
            response = session.get(f"{cls.BASE_URL}/tess/{cls.WORK}.hocr")
            assert response.status_code == 200, response.status_code
            cls.hocr_data = response.content

            response = session.get(f"{cls.BASE_URL}/max/{cls.WORK}.jpg")
            assert response.status_code == 200, response.status_code
            cls.jpg_data = response.content

    def _generate_files(self, directory: Path, *, skip_hocr: bool = False) -> None:
        hocr_file = directory / f"{self.WORK}.hocr"
        jpg_file = directory / f"{self.WORK}.jpg"

        if not skip_hocr:
            hocr_file.write_bytes(self.hocr_data)
            self.assertLess(1, hocr_file.stat().st_size)

        jpg_file.write_bytes(self.jpg_data)
        self.assertLess(1, jpg_file.stat().st_size)

    def _check_content(self, pdf_path: Path, key: str) -> None:
        self.assertLess(1, pdf_path.stat().st_size)

        with PdfReader(pdf_path) as reader:
            self.assertEqual(1, len(reader.pages))
            self.assertIn(key, reader.pages[0].extract_text())

    def test_export_pdf(self) -> None:
        with TemporaryDirectory() as temp_directory:
            directory = Path(temp_directory)
            self._generate_files(directory)

            pdf_path = directory / f"{self.WORK}.pdf"
            hocr_pdf.export_pdf(directory=str(directory), savefile=str(pdf_path))
            self._check_content(pdf_path, "tribunali")

    def test_export_pdf__kraken(self) -> None:
        with TemporaryDirectory() as temp_directory:
            directory = Path(temp_directory)
            self._generate_files(directory, skip_hocr=True)

            hocr_source_path = self.get_data_file("hocr_pdf/kraken.hocr")
            hocr_path = directory / f"{self.WORK}.hocr"
            hocr_path.write_bytes(Path(hocr_source_path).read_bytes())

            pdf_path = directory / f"{self.WORK}-saved.pdf"
            hocr_pdf.export_pdf(directory=str(directory), savefile=str(pdf_path))
            self._check_content(pdf_path, "Hello World")
            self._check_content(pdf_path, "formé\nuuuuu")

    def test_export_pdf__page_size(self) -> None:
        with TemporaryDirectory() as temp_directory:
            directory = Path(temp_directory)
            self._generate_files(directory)

            image_path = directory / f"{self.WORK}.jpg"
            image: Image.Image = Image.new(mode="RGB", size=(2458, 3150), color=(0, 0, 0))
            image.save(image_path)

            pdf_path = directory / f"{self.WORK}-saved.pdf"
            hocr_pdf.export_pdf(directory=str(directory), savefile=str(pdf_path))
            self._check_content(pdf_path, "tribunali")

            with PdfReader(pdf_path) as reader:
                size: RectangleObject = reader.pages[0].mediabox
                self.assertEqual((589, 756), size.upper_right)

    def test_main(self) -> None:
        with TemporaryDirectory() as temp_directory:
            directory = Path(temp_directory)
            self._generate_files(directory)

            with mock.patch("sys.argv", ["hocr-pdf", str(directory), "--savefile", str(directory / "output.pdf")]):
                hocr_pdf.main()
