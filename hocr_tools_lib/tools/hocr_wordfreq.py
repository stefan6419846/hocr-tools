"""
Calculate the word frequency inside an hOCR file.
"""

from __future__ import annotations

import os
import sys
import re
import argparse
from typing import cast, Callable, Generator

from lxml import html


def word_frequencies(
        hocr_in: os.PathLike[str] | str, case_insensitive: bool = False, spaces: bool = False, dehyphenate: bool = False,
        max_hits: int = 10
) -> Generator[str, None, None]:
    """
    Determine the word frequencies.

    :param hocr_in: hOCR file to analyze.
    :param case_insensitive: Ignore the casing of the words.
    :param spaces: Split on spaces only.
    :param dehyphenate: Try to dehyphenate the text.
    :param max_hits: Number of hits to return.
    :return: Up to `max_hits` of the most used words.
    """
    doc = html.parse(hocr_in)
    body = doc.find('body')
    assert body is not None
    text = body.text_content().strip()
    if case_insensitive:
        text = text.lower()
    if dehyphenate:
        # Delete blank lines.
        text = re.sub(r"^\s*$\r?\n", "", text)
        # Dehyphenate.
        text = re.sub(r"-\r?\n", "", text)
        # Replace line breaks with a space.
        text = re.sub(r"\r?\n", " ", text)
    word_counts: dict[str, int] = {}
    separators = re.compile(r'\W+', re.UNICODE)
    if spaces:
        separators = re.compile(r'\s+', re.UNICODE)
    for word in separators.split(text):
        if word == '':
            continue
        word_counts[word] = word_counts[word] + 1 if word in word_counts else 1

    for idx, word in enumerate(
            sorted(word_counts, reverse=True, key=cast(Callable[[str], int], word_counts.get))
    ):
        if idx > max_hits:
            break
        yield f"{word_counts[word]:<5d}\t{word}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Calculate word frequency in an hOCR file'
    )
    parser.add_argument(
        '-i',
        '--case-insensitive',
        action='store_true',
        default=False,
        help="ignore case"
    )
    parser.add_argument(
        '-s',
        '--spaces',
        action='store_true',
        default=False,
        help="split on spaces only"
    )
    parser.add_argument(
        '-y',
        '--dehyphenate',
        action='store_true',
        default=False,
        help="try to dehyphenate the text before analysis"
    )
    parser.add_argument(
        '-n',
        '--max',
        type=int,
        default=10,
        help="number of hits (default: %(default)s)"
    )
    parser.add_argument(
        'hocr_in',
        help="hOCR file to count frequency for (default: standard input)",
        type=argparse.FileType('r'),
        nargs='?',
        default=sys.stdin
    )
    args = parser.parse_args()

    results = word_frequencies(
        hocr_in=args.hocr_in, case_insensitive=args.case_insensitive,
        spaces=args.spaces, dehyphenate=args.dehyphenate, max_hits=args.max
    )
    print('\n'.join(results))

    args.hocr_in.close()
