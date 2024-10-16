"""
Split an hOCR file into individual pages.
"""

from __future__ import annotations

import argparse
import re
from os import PathLike

from lxml import etree, html


def split(hocr: PathLike[str] | str, pattern: str = "base-%03d.html") -> None:
    """
    Split the given hOCR file into multiple pages.

    :param hocr: hOCR file to split.
    :param pattern: Naming pattern for the output files.
    """
    assert re.search('%[0-9]*d', pattern)

    doc = etree.parse(hocr, html.XHTMLParser())
    pages = doc.xpath("//*[@class='ocr_page']")
    assert pages != []

    container = pages[0].getparent()
    index = 1
    for new_page in pages:
        container_pages = container.xpath("//*[@class='ocr_page']")
        for page in container_pages:
            container.remove(page)
        container.append(new_page)
        doc.write((pattern % index), pretty_print=True)
        index += 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="split a multipage hOCR file into single pages"
    )
    parser.add_argument("file", help="hOCR file", type=argparse.FileType('r'))
    parser.add_argument(
        "pattern", help="naming pattern, e.g. 'base-%%03d.html'"
    )
    args = parser.parse_args()

    split(hocr=args.file, pattern=args.pattern)

    args.file.close()
