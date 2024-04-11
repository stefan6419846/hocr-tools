"""
Extract the images and text within all the requested elements
within the hOCR file.
"""

from __future__ import annotations

import argparse
import ast
import os
import sys
from typing import cast, Tuple  # TODO: Drop `Tuple` after dropping Python 3.8.

from lxml import html
from PIL import Image

from hocr_tools_lib.utils.node_utils import get_prop, get_text
from hocr_tools_lib.utils.typing_utils import SupportsReadClose


def extract_images(
        hocr: SupportsReadClose[str], basename: str, pattern: str = "line-%03d.png", element: str = "ocr_line",
        pad: str | None = None, unicode_dammit: bool = False
) -> None:
    """
    Extract the images from the given document.

    :param hocr: hOCR file to use.
    :param basename: Image directory.
    :param pattern: Output file pattern to use.
    :param element: hOCR element to look into.
    :param pad: Extra padding for bounding box. If set, either one number for
                all four sides or four numbers separated by a comma.
    :param unicode_dammit: Attempt to use BeautifulSoup.UnicodeDammit for
                           fixing encoding issues.
    """
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
        from bs4 import UnicodeDammit  # type: ignore[attr-defined]
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
            assert image_name
        if basename:
            image_name = os.path.join(basename, os.path.basename(image_name))
        if not os.path.exists(image_name):
            raise FileNotFoundError(image_name)
        image = Image.open(image_name)
        lines = page.xpath(f"//*[@class='{element}']")
        line_count = 1
        for line in lines:
            bbox_prop = get_prop(line, 'bbox')
            assert bbox_prop
            bbox = [int(x) for x in bbox_prop.split()]
            if padding is not None:
                w, h = image.size
                bbox[0] = max(bbox[0] - padding[0], 0)
                bbox[1] = max(bbox[1] - padding[1], 0)
                bbox[2] = min(bbox[2] + padding[2], w)
                bbox[3] = min(bbox[3] + padding[3], h)
            if bbox[0] > bbox[2] or bbox[1] >= bbox[3]:
                continue
            line_image = image.crop(cast(Tuple[int, int, int, int], tuple(bbox)))
            line_image.save(pattern % line_count)
            with open(
                    txt_pattern % line_count, mode='w', encoding='utf-8'
            ) as fd:
                fd.write(get_text(line))
            line_count += 1
        image.close()


def main() -> None:
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
