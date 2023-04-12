"""
Extract the text within all the ocr_line elements within the hOCR file.
"""

import argparse
import re
import sys

from lxml import html


def lines(hocr):
    doc = html.parse(hocr)

    for line in doc.xpath("//*[@class='ocr_line']"):
        yield re.sub(r'\s+', '\x20', line.text_content()).strip()


def main():
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
