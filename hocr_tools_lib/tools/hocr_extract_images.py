"""
Extract the images and text within all the ocr_line elements
within the hOCR file.
"""

import argparse
import ast
import os
import sys

from lxml import html
from PIL import Image

from hocr_tools_lib.utils.node_utils import get_prop, get_text


def extract_images(
        hocr, basename, pattern="line-%03d.png", element="ocr_line",
        pad=None, unicode_dammit=False
):
    padding = None
    if pad is not None:
        padding = ast.literal_eval("[" + pad + "]")
        assert len(padding) in {1, 4}, (pad, padding)
        if len(padding) == 1:
            padding = padding * 4

    txt_pattern = pattern + '.txt'
    if pattern[-4] == '.':
        txt_pattern = pattern[:-3] + 'txt'

    if unicode_dammit:
        from bs4 import UnicodeDammit
        content = hocr.read()
        doc = UnicodeDammit(content, is_html=True)
        parser = html.HTMLParser(encoding=doc.original_encoding)
        doc = html.document_fromstring(content.encode('UTF-8'), parser=parser)
    else:
        doc = html.parse(hocr)

    pages = doc.xpath('//*[@class="ocr_page"]')
    for page in pages:
        image_name = get_prop(page, 'file', strip_value=True)
        if not image_name:
            image_name = get_prop(page, 'image', strip_value=True)
        if basename:
            image_name = os.path.join(basename, os.path.basename(image_name))
        if not os.path.exists(image_name):
            raise FileNotFoundError(image_name)
        image = Image.open(image_name)
        lines = page.xpath(f"//*[@class='{element}']")
        line_count = 1
        for line in lines:
            bbox = [int(x) for x in get_prop(line, 'bbox').split()]
            if padding is not None:
                w, h = image.size
                bbox[0] = max(bbox[0] - padding[0], 0)
                bbox[1] = max(bbox[1] - padding[1], 0)
                bbox[2] = min(bbox[2] + padding[2], w)
                bbox[3] = min(bbox[3] + padding[3], h)
            if bbox[0] > bbox[2] or bbox[1] >= bbox[3]:
                continue
            line_image = image.crop(bbox)
            line_image.save(pattern % line_count)
            with open(
                    txt_pattern % line_count, mode='w', encoding='utf-8'
            ) as fd:
                fd.write(get_text(line))
            line_count += 1
        image.close()


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Extract the images and texts within all the ocr_line "
            "elements within the hOCR file"
        )
    )
    parser.add_argument(
        "file",
        help="hOCR file",
        type=argparse.FileType('r'),
        nargs='?',
        default=sys.stdin
    )
    parser.add_argument("-b", "--basename", help="image-dir")
    parser.add_argument(
        "-p",
        "--pattern",
        help="file-pattern, default: %(default)s",
        default="line-%03d.png"
    )
    parser.add_argument(
        "-e",
        "--element",
        help="element-name, default: %(default)s",
        default="ocr_line"
    )
    parser.add_argument(
        "-P",
        "--pad",
        default=None,
        help="extra padding for bounding box"
    )
    parser.add_argument(
        "-U",
        "--unicodedammit",
        action="store_true",
        help=(
            "attempt to use BeautifulSoup.UnicodeDammit to fix encoding "
            "issues"
        )
    )
    args = parser.parse_args()

    extract_images(
        hocr=args.file, basename=args.basename, pattern=args.pattern,
        element=args.element, pad=args.pad, unicode_dammit=args.unicodedammit
    )

    args.file.close()
