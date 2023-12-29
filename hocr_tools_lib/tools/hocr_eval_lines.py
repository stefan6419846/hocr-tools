import argparse
import logging

from lxml import html

from hocr_tools_lib.utils.edit_utils import edit_distance
from hocr_tools_lib.utils.node_utils import get_text
from hocr_tools_lib.utils.text_utils import normalize


logger = logging.getLogger(__name__)
del logging


def evaluate_lines(tfile, hfile, verbose=False):
    truth_lines = tfile.read().split('\n')
    actual_doc = html.parse(hfile)
    actual_lines = [
        get_text(node) for node in actual_doc.xpath("//*[@class='ocr_line']")
    ]

    truth_lines = [normalize(s) for s in truth_lines]
    truth_lines = [s for s in truth_lines if s != ""]
    actual_lines = [normalize(s) for s in actual_lines]
    actual_lines = [s for s in actual_lines if s != ""]

    remaining = [] + truth_lines
    ocr_errors = 0
    for actual_line in actual_lines:
        min_d = 999999
        min_i = -1
        for index in range(len(remaining)):
            true_line = remaining[index]
            d = edit_distance(true_line, actual_line, min_d)
            if d < min_d:
                min_d = d
                min_i = index
        if verbose and min_d > 0:
            logger.info("distance %s", min_d)
            logger.info("\t%s" + actual_line)
            logger.info("\t%s" + remaining[min_i])
        assert min_i >= 0
        del remaining[min_i]
        ocr_errors += min_d

    segmentation_errors = 0
    for s in remaining:
        segmentation_errors += len(s)

    return segmentation_errors, ocr_errors


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Compute statistics about the quality of the geometric "
            "segmentation at the level of the given OCR element"
        )
    )
    parser.add_argument(
        "tfile", help="text file with the true lines",
        type=argparse.FileType('r')
    )
    parser.add_argument(
        "hfile",
        help="hOCR file with the actually recognized lines",
        type=argparse.FileType('r')
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    segmentation_errors, ocr_errors = evaluate_lines(
        tfile=args.tfile, hfile=args.hfile, verbose=args.verbose
    )

    print("segmentation_errors", segmentation_errors)
    print("ocr_errors", ocr_errors)

    args.tfile.close()
    args.hfile.close()
