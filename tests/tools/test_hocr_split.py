from tempfile import TemporaryDirectory
from unittest import mock

from hocr_tools_lib.tools import hocr_split
from tests import chdir, TestCase


class HocrSplitTestCase(TestCase):
    def test_split(self) -> None:
        with TemporaryDirectory() as temp_directory:
            filename = self.get_data_file_copy(
                'hocr_split/test.hocr', temp_directory
            )
            directory = filename.parent

            with chdir(directory):
                hocr_split.split(hocr=filename, pattern='test-%003d.hocr')

            self.assertSetEqual(
                {'test-001.hocr', 'test-002.hocr'},
                {entry.name for entry in directory.glob('test-*hocr')}
            )

            test_001_hocr_content = (directory / 'test-001.hocr').read_text()
            test_002_hocr_content = (directory / 'test-002.hocr').read_text()
            self.assertEqual(
                1, test_001_hocr_content.count('ocr_page'),
                test_001_hocr_content
            )
            self.assertEqual(
                1, test_002_hocr_content.count('ocr_page'),
                test_002_hocr_content
            )

            # Only once, see issue #58.
            self.assertEqual(
                1, test_001_hocr_content.count('xml:lang='),
                test_001_hocr_content
            )
            self.assertEqual(
                1, test_001_hocr_content.count('xmlns='),
                test_001_hocr_content
            )

    def test_main(self) -> None:
        with TemporaryDirectory() as directory:
            filename = self.get_data_file_copy(
                'hocr_split/test.hocr', directory
            )

            with mock.patch(
                    'sys.argv',
                    ['hocr-split', str(filename), 'test-%003d.hocr']
            ):
                with chdir(directory):
                    hocr_split.main()
