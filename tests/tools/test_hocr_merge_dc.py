import contextlib
from io import StringIO
from unittest import mock

from hocr_tools_lib.tools import hocr_merge_dc
from tests import TestCase


class HocrMergeDcTestCase(TestCase):
    def test_merge_dc(self):
        sample_html = self.get_data_file('sample.html')
        dcsample_xml = self.get_data_file('hocr_merge_dc/dcsample2.xml')

        merged = hocr_merge_dc.merge_dc(dc=dcsample_xml, hocr=sample_html)

        sample_html_content = self.get_data_content('sample.html')
        self.assertIn(
            b"name='DC.title' content='Alice im Wonderland'",
            sample_html_content
        )
        self.assertNotIn(
            b"name='DC.title' content='UKOLN'",
            sample_html_content
        )
        self.assertIn(
            b'name="DC.title" content="UKOLN"',
            merged
        )

    def test_main(self):
        sample_html = self.get_data_file('sample.html')
        dcsample_xml = self.get_data_file('hocr_merge_dc/dcsample2.xml')

        stdout = StringIO()
        with mock.patch(
                'sys.argv',
                ['hocr-merge-dc', dcsample_xml, sample_html]
        ):
            with contextlib.redirect_stdout(stdout):
                hocr_merge_dc.main()
