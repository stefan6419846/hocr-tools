import subprocess
from tempfile import TemporaryDirectory
from unittest import mock

from hocr_tools_lib.tools import hocr_extract_images
from tests import chdir, TestCase


class HocrExtractImagesTestCase(TestCase):
    def _check(self, level, basename, expected_count, stdin, extra_args=''):
        with TemporaryDirectory() as directory:
            tess_hocr = self.get_data_file_copy('tess.hocr', directory)
            self.get_data_file_copy('alice_1.png', directory)
            directory = tess_hocr.parent
            if stdin:
                command = [
                    f'cat "{tess_hocr!s}" | hocr-extract-images{extra_args} -p "{basename}-%03d.png" -b "{directory!s}" -e "{level}"'  # noqa: E501
                ]
            else:
                command = [
                    'hocr-extract-images', extra_args, '-p', f'{basename}-%03d.png', '-b', str(directory), '-e', level, str(tess_hocr)  # noqa: E501
                ]
                command = [x for x in command if x]

            subprocess.check_call(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=stdin, cwd=directory
            )

            png_files = [
                path.name for path in directory.glob(f'{basename}*png')
            ]
            self.assertEqual(expected_count, len(png_files), png_files)

            txt_files = [
                path.name for path in directory.glob(f'{basename}*txt')
            ]
            self.assertEqual(expected_count, len(txt_files), txt_files)

    def test_result_file_count(self):
        for level, basename, expected_count in [
                ('ocr_page', 'page', 1),
                ('ocr_line', 'line', 37),
                ('ocrx_word', 'word', 503),
        ]:
            with self.subTest(level=level, stdin=False):
                self._check(
                    level=level, basename=basename,
                    expected_count=expected_count,
                    stdin=False
                )

            with self.subTest(level=level, stdin=True):
                self._check(
                    level=level, basename=basename,
                    expected_count=expected_count,
                    stdin=True
                )

    def test_unicode_dammit(self):
        filename = self.get_data_file('sample.txt')
        stdout = subprocess.check_output(
            ['wc', '-w', filename]
        )
        self.assertEqual(503, int(stdout.split()[0]))

        for stdin in [True, False]:
            with self.subTest(stdin=stdin):
                self._check(
                    level='ocrx_word', basename='word', expected_count=503,
                    extra_args='', stdin=stdin,
                )

    def test_main(self):
        with TemporaryDirectory() as directory:
            tess_hocr = self.get_data_file_copy('tess.hocr', directory)
            self.get_data_file_copy('alice_1.png', directory)
            command = [
                'hocr-extract-images', '-p', 'word-%03d.png', '-b', directory, '-e', 'ocrx_word', str(tess_hocr)  # noqa: E501
            ]

            with mock.patch('sys.argv', command):
                with chdir(directory):
                    hocr_extract_images.main()
