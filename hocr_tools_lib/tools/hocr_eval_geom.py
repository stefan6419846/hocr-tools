"""
Compute statistics about the quality of the geometric
segmentation at the level of the given hOCR element.
"""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from typing import Generator

from lxml import html

from hocr_tools_lib.utils.node_utils import get_bbox
from hocr_tools_lib.utils.rectangle_utils import overlaps, relative_overlap, RectangleType


@dataclass
class Boxstats:
    multiple: int = 0
    """
    Number of boxes with more than one significant overlap.
    """

    missing: int = 0
    """
    Number of boxes with no close match.
    """

    error: float = 0.0
    """
    Aggregated relative overlap for close matches.
    """

    count: int = 0
    """
    Total number of of boxes.
    """

    def to_tuple(self) -> tuple[int, int, float, int]:
        """
        Convert to a tuple.

        :return: The values ``(multiple, missing, error, count)``.
        """
        return (self.multiple, self.missing, self.error, self.count)


def boxstats(
        truths: list[RectangleType | None],
        actuals: list[RectangleType | None],
        significant_overlap: float = 0.1,
        close_match: float = 0.9
) -> Boxstats:
    """
    Determine the box statistics for the given set of boxes.

    :param truths: Ground truth boxes.
    :param actuals: Actual boxes.
    :param significant_overlap: Lower bound for a significant overlap.
    :param close_match: Lower bound for an overlap.
    :return: The corresponding statistics.
    """
    result = Boxstats()
    for t in truths:
        overlapping = [a for a in actuals if overlaps(a, t)]
        oas = [relative_overlap(t, a) for a in overlapping]
        if len([o for o in oas if o > significant_overlap]) > 1:
            result.multiple += 1
        matching = [o for o in oas if o > close_match]
        if len(matching) < 1:
            result.missing += 1
        elif len(matching) > 1:
            raise AttributeError(
                "Multiple close matches: your segmentation files are bad"
            )
        else:
            result.error += 1.0 - matching[0]
            result.count += 1
    return result


def check_bad_partition(boxes: list[RectangleType | None], significant_overlap: float = 0.1) -> bool:
    """
    Check if the given boxes are badly partitioned as they overlap too much.

    :param boxes: The boxes to check.
    :param significant_overlap: Lower bound for a significant overlap.
    :return: Whether the partitioning is badly done.
    """
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if relative_overlap(boxes[i], boxes[j]) > significant_overlap:
                return True
    return False


def evaluate_geometries(
        truth: os.PathLike[str], actual: os.PathLike[str], element: str = 'ocr_line',
        significant_overlap: float = 0.1, close_match: float = 0.9
) -> Generator[tuple[Boxstats, Boxstats], None, None]:
    """
    Evaluate the geometries for the given files.

    :param truth: hOCR file with ground truth.
    :param actual: hOCR file with actual data.
    :param element: hOCR element to look at.
    :param significant_overlap: Lower bound for a significant overlap.
    :param close_match: Lower bound for an overlap.
    :return: For each set of pages, a tuple of the statistics checking the
             actual values against the truth values and vice versa.
    """
    # Read the hOCR files.
    truth_doc = html.parse(truth)
    actual_doc = html.parse(actual)
    truth_pages = truth_doc.xpath("//*[@class='ocr_page']")
    actual_pages = actual_doc.xpath("//*[@class='ocr_page']")
    assert len(truth_pages) == len(actual_pages)
    pages = zip(truth_pages, actual_pages)

    # Compute statistics.
    for truth_page, actual_page in pages:
        tobjs = truth_page.xpath(f"//*[@class='{element}']")
        aobjs = actual_page.xpath(f"//*[@class='{element}']")
        tboxes = [get_bbox(n) for n in tobjs]
        if check_bad_partition(tboxes, significant_overlap):
            raise ValueError(
                "Ground truth data is not an acceptable segmentation"
            )
        aboxes = [get_bbox(n) for n in aobjs]
        if check_bad_partition(aboxes, significant_overlap):
            raise ValueError("Actual data is not an acceptable segmentation")
        yield (
            boxstats(tboxes, aboxes, significant_overlap, close_match),
            boxstats(aboxes, tboxes, significant_overlap, close_match)
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Compute statistics about the quality of the geometric "
            "segmentation at the level of the given hOCR element"
        ),
        epilog=(
            "The output is a 4-tuple (multiple,missing,error,count) "
            "for the truth compared with the actual and then again "
            "another 4-tuple in the other direction"
        )
    )
    parser.add_argument(
        "truth", help="hOCR file with ground truth",
        type=argparse.FileType('r')
    )
    parser.add_argument(
        "actual",
        help="hOCR file from the actual recognition",
        type=argparse.FileType('r')
    )
    parser.add_argument(
        "-e",
        "--element",
        default="ocr_line",
        help="hOCR element to look at, default: %(default)s"
    )
    parser.add_argument(
        "-o",
        "--significant_overlap",
        type=float,
        default=0.1,
        help="default: %(default)s"
    )
    parser.add_argument(
        "-c",
        "--close_match",
        type=float,
        default=0.9,
        help="default: %(default)s"
    )
    args = parser.parse_args()

    results = evaluate_geometries(
        truth=args.truth, actual=args.actual, element=args.element,
        significant_overlap=args.significant_overlap,
        close_match=args.close_match
    )

    for result in results:
        truth_stats, actual_stats = result
        print(truth_stats.to_tuple(), actual_stats.to_tuple())

    args.truth.close()
    args.actual.close()
