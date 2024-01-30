from __future__ import annotations

from typing import cast

from lxml import html

from hocr_tools_lib.utils import node_utils
from tests import TestCase


class GetPropTestCase(TestCase):
    @classmethod
    def get_div(cls, value: str) -> html.HtmlElement:
        if value.startswith('"'):
            string = f"<div class='ocr_page' id='page_1' title='image {value}; bbox 0 0 2488 3507; ppageno 0'>"
        else:
            string = f'<div class="ocr_page" id="page_1" title="image {value}; bbox 0 0 2488 3507; ppageno 0">'
        element = html.document_fromstring(string)
        return cast(html.HtmlElement, list(element.xpath('//div'))[0])

    def test_strip_value(self) -> None:
        for input_value in ["'alice_1.png'", '"alice_1.png"', 'alice_1.png']:
            with self.subTest(input_value=input_value):
                div = self.get_div(input_value)
                self.assertEqual('alice_1.png', node_utils.get_prop(node=div, name='image', strip_value=True))
