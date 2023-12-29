#!/usr/bin/env python

"""
Check the given file for conformance with the hOCR format spec.
"""

import argparse
import sys

from lxml import html

from hocr_tools_lib.utils.node_utils import get_bbox, get_prop
from hocr_tools_lib.utils.rectangle_utils import mostly_non_overlapping


class Checker:
    test_counter = 0

    def __init__(self, hocr_file, no_overlap=False):
        """
        :param hocr_file: hOCR file to check.
        :param no_overlap: Disable the overlap checks.
        """
        self.test_counter = 0
        self.no_overlap = no_overlap
        self.doc = html.parse(hocr_file)

    def test_ok(self, v, msg):
        self.test_counter += 1
        if not v:
            sys.stderr.write("not ")
        sys.stderr.write("ok " + str(self.test_counter) + " - " + msg + "\n")

    def check(self):
        self.check_xml_structure()
        if not self.no_overlap:
            self.check_geometry()

        # FIXME add many other checks:
        # - containment of paragraphs, careas, etc.
        # - ocr-capabilities vs. actual tags
        # - warn about text outside ocr_ elements
        # - check title= attribute format
        # - check that only the right attributes are present on the right
        #   elements
        # - check for unrecognized ocr_ elements
        # - check for significant overlaps
        # - check that image files are not repeated

    def check_xml_structure(self):
        # Check for presence of meta information.
        self.test_ok(
            self.doc.xpath("//meta[@name='ocr-system']") != [],
            "//meta[@name='ocr-system']"
        )
        self.test_ok(
            self.doc.xpath("//meta[@name='ocr-capabilities']") != [],
            "//meta[@name='ocr-capabilities']"
        )

        # Check for presence of page.
        self.test_ok(
            self.doc.xpath("//*[@class='ocr_page']") != [], "has a page"
        )

        # Check that lines are inside pages.
        lines = self.doc.xpath("//*[@class='ocr_line']")
        for line_idx, line in enumerate(lines):
            self.test_ok(
                line.xpath("./ancestor::*[@class='ocr_page']"),
                f"ocr_line {line_idx:2d} in an ocr_page"
            )

        # Check that pars are inside pages.
        pars = self.doc.xpath("//*[@class='ocr_par']")
        for par_idx, par in enumerate(pars):
            self.test_ok(
                par.xpath("./ancestor::*[@class='ocr_page']"),
                f"ocr_par {par_idx:2d} in an ocr_page"
            )

        # Check that careas are inside pages.
        careas = self.doc.xpath("//*[@class='ocr_carea']")
        for carea_idx, carea in enumerate(careas):
            self.test_ok(
                carea.xpath("./ancestor::*[@class='ocr_page']"),
                f"ocr_carea {carea_idx:2d} in an ocr_page"
            )

    def check_geometry(self):
        for page in self.doc.xpath("//*[@class='ocr_page']"):
            # Check lines.
            objs = page.xpath("//*[@class='ocr_line']")
            line_bboxes = [
                get_bbox(obj) for obj in objs if get_prop(obj, 'bbox')
            ]
            self.test_ok(
                mostly_non_overlapping(line_bboxes),
                'mostly_nonoverlapping/line'
            )
            # Check paragraphs.
            objs = page.xpath("//*[@class='ocr_par']")
            par_bboxes = [
                get_bbox(obj) for obj in objs if get_prop(obj, 'bbox')
            ]
            self.test_ok(
                mostly_non_overlapping(par_bboxes), 'mostly_nonoverlapping/par'
            )
            # Check careas.
            objs = page.xpath("//*[@class='ocr_carea']")
            carea_bboxes = [
                get_bbox(obj) for obj in objs if get_prop(obj, 'bbox')
            ]
            self.test_ok(
                mostly_non_overlapping(carea_bboxes),
                'mostly_nonoverlapping/carea'
            )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Check the given file for conformance with the hOCR format spec"
        )
    )
    parser.add_argument(
        "file",
        help="hOCR file to check",
        type=argparse.FileType('r'),
        nargs='?',
        default=sys.stdin
    )
    parser.add_argument(
        "-o",
        "--nooverlap",
        help="Disable the overlap checks",
        action="store_true"
    )
    args = parser.parse_args()

    checker = Checker(hocr_file=args.file, no_overlap=args.nooverlap)
    checker.check()

    args.file.close()
