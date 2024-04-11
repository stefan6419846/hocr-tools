"""
Extract the text within all the ``ocr_line`` elements within the hOCR file.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from typing import Generator

from lxml import html


def lines(hocr: os.PathLike[str]) -> Generator[str, None, None]:
    """
    Extract the lines from the given document.

    :param hocr: hOCR file to extract from.
    :return: The corresponding lines.
    """
    doc = html.parse(hocr)

    for line in doc.xpath("//*[@class='ocr_line']"):
        yield re.sub(r'\s+', '\x20', line.text_content()).strip()


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            'extract the text within all the ocr_line elements '
            'within the hOCR file'
        )
    )
    parser.add_argument('file', nargs='?', default=sys.stdin)
    args = parser.parse_args()

    result = lines(hocr=args.file)
    print('\n'.join(result))
