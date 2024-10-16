"""
Cut a page (horizontally) into two pages in the middle
such that the most of the bounding boxes are separated
nicely, e.g. cutting double pages or double columns.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys

from lxml import html
from PIL import Image, ImageDraw

from hocr_tools_lib.utils.node_utils import get_bbox, get_prop


logger = logging.getLogger(__name__)
del logging


def cut(hocr: os.PathLike[str], debug: bool = False) -> None:
    """
    Cut the given hOCR file.

    Generates an image file for both columns with the same basename
    as the input file, only adding the suffix `.left` and `.right`
    before the extension.

    :param hocr: hOCR file to cut.
    :param debug: Create a third image file with the suffix `.cut`
                  with some debugging output.
    """
    doc = html.parse(hocr)

    pages = doc.xpath("//*[@class='ocr_page']")

    for page in pages:
        filename = get_prop(page, 'image')
        assert filename is not None
        filename = os.path.join(os.path.dirname(hocr), filename)
        try:
            image = Image.open(filename)
            debug_image = Image.open(filename)
            dr = ImageDraw.Draw(debug_image)
            image_found = True
        except IOError:
            logger.warning("Warning: Image %s not found!", filename)
            debug = False
            image_found = False

        bbox = get_bbox(page)
        assert bbox is not None
        middle = bbox[2] / 2

        left_ends = []
        right_starts = []
        for line in doc.xpath("//*[@class='ocr_line']"):
            b = get_bbox(line)
            assert b is not None
            if b[0] > middle:
                pos = "right"
            elif b[2] < middle:
                pos = "left"
            elif b[2] - middle > middle - b[1]:
                pos = "right"
            else:
                pos = "left"
            if pos == "right":
                right_starts.append(b[0])
                if debug:
                    dr.rectangle(b, fill=32)
            else:
                left_ends.append(b[2])
                if debug:
                    dr.rectangle(b, fill=96)

        left_ends.sort()
        right_starts.sort()
        n = len(left_ends)
        m = len(right_starts)
        middle_left = left_ends[n // 2]
        middle_right = right_starts[m // 2]

        middle = int((middle_left + middle_right) / 2)
        logger.info("Cutting at %s", middle)

        if image_found:
            if filename[-4] == ".":
                name = filename[:-3]
                suffix = filename[-3:]
            else:
                name = filename
                suffix = ""

            if debug:
                dr.line(
                    (middle_left, 0, middle_left, debug_image.size[1]),
                    fill=64,
                    width=3
                )
                dr.line(
                    (middle_right, 0, middle_right, debug_image.size[1]),
                    fill=64,
                    width=3
                )
                dr.line(
                    (middle, 0, middle, debug_image.size[1]), fill=128, width=5
                )
                debug_output = name + "cut." + suffix
                debug_image.save(debug_output)
                logger.info("Debug output is saved in %s", debug_output)

            left = image.crop((0, 0, middle, image.size[1]))
            left_name = name + "left." + suffix
            left.save(left_name)
            logger.info("Left page is saved in %s", left_name)
            right = image.crop((middle, 0, image.size[0], image.size[1]))
            right_name = name + "right." + suffix
            right.save(right_name)
            logger.info("Right page is saved in %s", right_name)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            'Cut a page (horizontally) into two pages in the middle '
            'such that the most of the bounding boxes are separated '
            'nicely, e.g. cutting double pages or double columns'
        )
    )
    parser.add_argument('file', nargs='?', default=sys.stdin)
    parser.add_argument('-d', '--debug', action="store_true")
    args = parser.parse_args()

    cut(hocr=args.file, debug=args.debug)
