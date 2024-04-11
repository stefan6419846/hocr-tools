"""
Extract lines from Google 1000 book sample.
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import sys
import xml.sax
from dataclasses import dataclass
from typing import cast, Any, Callable

from PIL import Image

from hocr_tools_lib.utils.node_utils import get_prop


USAGE = """
%(prog)s hocr image_pattern output_prefix

Process Google 1000 books volumes and prepares line or word images
for alignment using OCRopus.

Run ocroscript align-... Volume_0000/0000/0000.{png,txt}

Arguments:

    hocr: hOCR source file

    image_pattern: either a glob pattern that results in a list
        of image files in order, or @filename for a file containing
        a list of image files in order; DON'T FORGET TO QUOTE THIS

    output_pattern: output images are of the form
        output_pattern%%(pageno,lineno)

Environment Variables:

    element="ocr_line": which element to extract; ocrx_word and
        ocr_cinfo are also useful

    regex=".": the text for any transcription must match this pattern

    dict=None: a dictionary; if provided, all the words in any line
        that's output by the program must occur in the dictionary

    min_len=20: minimum length of text for which lines are output

    max_len=50: maximum length of text for which lines are output

    max_lines=1000000: maximum number of lines output

    pad=2: pad the bounding box by this many pixels prior to extraction

    output_format=png: format for line image files
"""


def extract_g1000(hocr: str, image_pattern: str, output_prefix: str) -> None:
    """
    Perform the extraction itself.

    :param hocr: hOCR source file.
    :param image_pattern: Either a glob pattern that results in a list of image
                          files in order, or ``@filename`` for a file containing
                          a list of image files in order.
    :param output_prefix: Output images are of the form
                          ``output_pattern % (pageno, lineno)``.
    """
    if not os.path.exists(hocr):
        sys.stderr.write(hocr + ": not found")
        sys.exit(1)

    parser = xml.sax.make_parser()
    with os.popen(
            f"tidy -q -wrap 9999 -asxhtml < {hocr} 2> /tmp/tidy_errs", "r"
    ) as stream:
        configuration = get_configuration()
        handler = DocumentHandler(
            output_pattern=output_prefix,
            image_list=get_image_list(image_pattern),
            configuration=configuration
        )
        parser.setContentHandler(handler)
        parser.parse(stream)  # type: ignore[no-untyped-call]


def get_image_list(image_pattern: str) -> list[str]:
    """
    Get the list of images for the given pattern.

    See :func:`~extract_g1000` for the format.

    :param image_pattern: The input file pattern.
    :return: The corresponding image files.
    """
    if image_pattern[0] == "@":
        with open(image_pattern[1:]) as fd:
            image_list = fd.readlines()
        image_list = [s[:-1] for s in image_list]
        image_list.sort()
    else:
        image_list = glob.glob(image_pattern)
    return image_list


@dataclass
class Configuration:
    """
    Configuration for the configuration values.
    """

    element: str = 'ocr_line'
    """
    hOCR element to look at.
    """

    regex: str = '.'
    """
    The text for any transcription must match this pattern.
    """

    min_len: int = 20
    """
    Minimum length of text to output the lines for.
    """

    max_len: int = 50
    """
    Maximum length of text to output the lines for.
    """

    dict_data: dict[str, int] | None = None
    """
    Optional: Custom dictionary to use for filtering the texts.
    """

    dict_file: str = ''
    """
    Dictionary file holding a word in each line.
    """

    max_lines: int = 1000000
    """
    Maximum number of lines for the output.
    """

    pad: int = 2
    """
    Pad the bounding box by this number of pixels prior to extraction.
    """

    output_format: str = 'png'
    """
    Format of the line image files.
    """


def get_configuration() -> Configuration:
    """
    Get the configuration from environment variables.

    :return: The corresponding configuration.
    """
    def set_value_if_available(key: str, name: str | None = None, parser: Callable[[str], Any] | None = None) -> None:
        name = name or key
        value_ = os.getenv(key)
        if not value_:
            return
        if parser:
            value_ = parser(value_)
        setattr(configuration, name, value_)

    configuration = Configuration()
    set_value_if_available('element')
    set_value_if_available('regex')
    set_value_if_available('min_len', parser=int)
    set_value_if_available('max_len', parser=int)
    set_value_if_available('dict', name='dict_file')
    set_value_if_available('max_lines', parser=int)
    set_value_if_available('pad', parser=int)
    set_value_if_available('output_format')

    if configuration.dict_file:
        stream = open(configuration.dict_file, "r")
        words = stream.read().split()
        stream.close()
        configuration.dict_data = {}
        for word in words:
            configuration.dict_data[word.lower()] = 1
        # print(
        #     f"[read {len(words):d} words from {configuration.dict_file}]\n"
        # )

    return configuration


def check_dict(dictionary: dict[str, Any], s: str) -> bool:
    """
    Check if all words of the given string are part of the dictionary.

    :param dictionary: The dictionary to check inside.
    :param s: The text whose words to check against the dictionary.
    :return: Whether all words are part of the dictionary.
    """
    if not dictionary:
        return True
    words = re.split(r'\W+', s)
    for word in words:
        if word == "":
            continue
        if not dictionary.get(word.lower()):
            return False
    return True


def write_string(filename: str, text: str) -> None:
    """
    Write the given text to the given file.

    :param filename: The file to write to.
    :param text: The text to write.
    """
    with open(filename, "wb") as stream:
        stream.write(text.encode("utf-8"))


class DocumentHandler(xml.sax.handler.ContentHandler):
    """
    hOCR document handler.
    """

    def __init__(self, output_pattern: str, image_list: list[str], configuration: Configuration) -> None:
        """
        :param output_pattern: The output pattern to use. See :func:`~extract_g1000` for details.
        :param image_list: The list of images to use.
        :param configuration: The configuration to use.
        """
        super().__init__()
        self.element = configuration.element
        self.regex = configuration.regex
        self.image_list = image_list
        self.configuration = configuration
        self.output_pattern = output_pattern

    def startDocument(self) -> None:  # noqa: N802
        self.total = 0
        self.pageno = -1
        self.text = ""
        self.depth = 0
        self.start = -1
        # self.copied: dict[] = {}

    def endDocument(self) -> None:  # noqa: N802
        pass

    def startElement(self, name: str, attrs: xml.sax.xmlreader.AttributesImpl) -> None:  # noqa: N802
        self.depth += 1
        if attrs.get("class", "") == "ocr_page":
            self.lineno = -1
            self.pageno += 1
            self.page = self.image_list[self.pageno]
            self.image = Image.open(self.page)
        if attrs.get("class", "") == self.element:
            self.lineno += 1
            props = attrs.get("title", None)
            if props is not None:
                self.bbox = get_prop(props, "bbox")  # type: ignore[arg-type]  # FIXME
            else:
                self.bbox = None
            self.start = self.depth
            self.text = ""

    def endElement(self, name: str) -> None:  # noqa: N802
        if self.depth == self.start:
            if self.configuration.min_len <= len(self.text) <= \
                    self.configuration.max_len and \
                    re.match(self.regex, self.text) and \
                    check_dict(cast(dict[str, Any], self.configuration.dict_data), self.text):
                print(self.page, self.bbox, self.text.encode("utf-8"))
                w, h = self.image.size
                assert self.bbox
                x0, y0, x1, y1 = [int(s) for s in self.bbox.split()]
                assert y0 < y1 and x0 < x1 <= w and y1 <= h
                x0 = max(0, x0 - self.configuration.pad)
                y0 = max(0, y0 - self.configuration.pad)
                x1 = min(w, x1 + self.configuration.pad)
                y1 = min(h, y1 + self.configuration.pad)
                limage = self.image.crop((x0, y0, x1, y1))
                base = self.output_pattern % (self.pageno, self.lineno)
                basedir = os.path.dirname(base)
                if not os.path.exists(basedir):
                    os.mkdir(basedir)
                limage.save(base + "." + self.configuration.output_format)
                limage.close()
                write_string(base + ".txt", self.text)
                write_string(base + ".bbox", self.bbox)
                self.total += 1
                if self.total >= self.configuration.max_lines:
                    sys.exit(0)
            self.text = ""
            self.start = -1
        self.depth -= 1

    def characters(self, text: str, start: int, end: int) -> None:  # type: ignore[override]
        if self.text is not None:
            self.text += text[start:end]


def main() -> None:
    parser = argparse.ArgumentParser(
        usage=USAGE,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('hocr')
    parser.add_argument('image_pattern')
    parser.add_argument('output_pattern')

    args = parser.parse_args()

    extract_g1000(
        hocr=args.hocr, image_pattern=args.image_pattern,
        output_prefix=args.output_prefix
    )
