"""
Extract lines from Google 1000 book sample.
"""

import argparse
import glob
import os
import re
import sys
import xml.sax
from dataclasses import dataclass

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


def extract_g1000(hocr, image_pattern, output_prefix):
    if not os.path.exists(hocr):
        sys.stderr.write(hocr + ": not found")
        sys.exit(1)

    parser = xml.sax.make_parser()
    stream = os.popen(
        f"tidy -q -wrap 9999 -asxhtml < {hocr} 2> /tmp/tidy_errs", "r"
    )
    configuration = get_configuration()
    handler = DocumentHandler(
        output_pattern=output_prefix,
        image_list=get_image_list(image_pattern),
        configuration=configuration
    )
    parser.parseFile(stream, handler)


def get_image_list(image_pattern):
    if image_pattern[0] == "@":
        with open(image_pattern[1:]) as fd:
            image_list = fd.readlines()
        image_list = [s[:-1] for s in image_list]
        image_list.sort()
    else:
        image_list = glob.glob(image_pattern)
    return image_list


def get_configuration():
    @dataclass
    class Configuration:
        element: str = 'ocr_line'
        regex: str = '.'
        min_len: int = 20
        max_len: int = 50
        dict_data = None
        dict_file: str = None
        max_lines: int = 1000000
        pad: int = 2
        output_format: str = 'png'

    def set_value_if_available(key, name=None, parser=None):
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


def check_dict(dictionary, s):
    if not dictionary:
        return True
    words = re.split(r'\W+', s)
    for word in words:
        if word == "":
            continue
        if not dictionary.get(word.lower()):
            return False
    return True


def write_string(file, text):
    stream = open(file, "w")
    stream.write(text.encode("utf-8"))
    stream.close()


class DocumentHandler(xml.sax.handler.ContentHandler):
    def __init__(self, output_pattern, image_list, configuration):
        super().__init__()
        self.element = configuration.element
        self.regex = configuration.regex
        self.image_list = image_list
        self.configuration = configuration
        self.output_pattern = output_pattern

    def startDocument(self):  # noqa: N802
        self.total = 0
        self.pageno = -1
        self.text = None
        self.depth = 0
        self.start = -1
        self.copied = {}

    def endDocument(self):  # noqa: N802
        pass

    def startElement(self, name, attrs):  # noqa: N802
        self.depth += 1
        if attrs.get("class", "") == "ocr_page":
            self.lineno = -1
            self.pageno += 1
            self.page = self.image_list[self.pageno]
            self.image = Image.open(self.page)
        if attrs.get("class", "") == self.element:
            self.lineno += 1
            props = attrs.get("title", "")
            self.bbox = get_prop(props, "bbox")
            self.start = self.depth
            self.text = ""

    def endElement(self, name):  # noqa: N802
        if self.depth == self.start:
            if self.configuration.min_len <= len(self.text) <= \
                    self.configuration.max_len and \
                    re.match(self.regex, self.text) and \
                    check_dict(dict, self.text):
                print(self.page, self.bbox, self.text.encode("utf-8"))
                w, h = self.image.size
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
            self.text = None
            self.start = -1
        self.depth -= 1

    def characters(self, text, start, end):
        if self.text is not None:
            self.text += text[start:end]


def main():
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
