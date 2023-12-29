import argparse
import logging

from lxml import html
from PIL import Image, ImageDraw

from hocr_tools_lib.utils.edit_utils import edit_distance, remove_tex
from hocr_tools_lib.utils.node_utils import get_bbox, get_text
from hocr_tools_lib.utils.rectangle_utils import area, erode, height, intersect, \
    width
from hocr_tools_lib.utils.text_utils import normalize


logger = logging.getLogger(__name__)
del logging

# Relative and absolute thresholds in vertical and horizontal direction.
HTOL = 90
VTOL = 80
HPIX = 5
VPIX = 5


def evaluate(truth, actual, img_file, debug=False, verbose=False):
    if img_file:
        im = Image.open(img_file)
        logger.info(
            "Image %s: size=%r, format=%r, mode=%r",
            img_file, im.size, im.format, im.mode
        )
        draw = ImageDraw.Draw(im)
    else:
        im = None

    # Get pages from inputs.
    truth_doc = html.parse(truth)
    actual_doc = html.parse(actual)

    # Parse pages.
    truth_pages = truth_doc.xpath("//*[@class='ocr_page']")
    actual_pages = actual_doc.xpath("//*[@class='ocr_page']")

    # Zip ground-truth and OCR result pages.
    assert len(truth_pages) == len(actual_pages)
    pages = zip(truth_pages, actual_pages)

    segmentation_errors = 0
    segmentation_ocr_errors = 0
    ocr_errors = 0

    for truth, actual in pages:
        true_lines = truth.xpath("//*[@class='ocr_line']")
        actual_lines = actual.xpath("//*[@class='ocr_line']")
        tx = [
            min(HPIX, (100 - HTOL) * width(get_bbox(line)) / 100)
            for line in true_lines
        ]
        ty = [
            min(VPIX, (100 - VTOL) * height(get_bbox(line)) / 100)
            for line in true_lines
        ]
        for index, true_line in enumerate(true_lines):
            bbox = get_bbox(true_line)
            bbox_small = erode(bbox, tx[index], ty[index])
            candidates = [
                (
                    area(intersect(get_bbox(line), bbox)), get_bbox(line),
                    get_text(line)
                ) for line in actual_lines
            ]
            q = 0
            tight_overlap = False
            if candidates:
                q, actual_bbox, actual_line = max(candidates)
                actual_bbox_small = erode(actual_bbox, tx[index], ty[index])
                if (
                        area(intersect(actual_bbox_small, bbox)) == area(
                            actual_bbox_small
                        ) and area(intersect(actual_bbox, bbox_small)) == area(
                            bbox_small
                        )
                ):
                    tight_overlap = True

            if tight_overlap == 0:
                if verbose:
                    logger.warning(
                        "segmentation_error: area_overlap = %s true_bbox %s",
                        q * 1.0 / area(bbox), bbox
                    )
                    logger.warning("\t%s", get_text(true_line))
                segmentation_errors += 1

                if candidates:
                    true_text = remove_tex(get_text(true_line))
                    segmentation_ocr_errors += edit_distance(
                        normalize(true_text), normalize(actual_line)
                    )
                else:
                    segmentation_ocr_errors += len(get_text(true_line))

                if img_file:
                    draw.rectangle(bbox, outline="#ff0000")
                    if candidates:
                        draw.rectangle(actual_bbox, outline="#0000ff")
                continue
            true_text = remove_tex(get_text(true_line))
            actual_text = actual_line
            if debug:
                logger.info("overlap %s true_bbox %s", q, bbox)
                logger.info("\t%s", true_text)
                logger.info("\t%s", actual_text)
            error = edit_distance(normalize(true_text), normalize(actual_text))
            if verbose and error > 0:
                logger.info("ocr_error %s true_bbox %s", error, bbox)
                logger.info("\t%s", true_text)
                logger.info("\t%s", actual_text)
            ocr_errors += error

    if img_file:
        im.save("errors.png")
        im.close()

    return im, segmentation_errors, segmentation_ocr_errors, ocr_errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "truth", help="hOCR file with ground truth",
        type=argparse.FileType('r')
    )
    parser.add_argument(
        "actual",
        help="hOCR file from the actual recognition",
        type=argparse.FileType('r')
    )
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    # Not yet supported:
    # parser.add_argument(
    #     "-e", "--element", default="ocr_line", help="%(default)s"
    # )
    # parser.add_argument(
    #     "-o", "--significant_overlap", type=float, default=0.1,
    #     help="default: %(default)s"
    # )
    parser.add_argument("-i", "--imgfile", type=argparse.FileType('r'))
    args = parser.parse_args()

    image, segmentation_errors, segmentation_ocr_errors, ocr_errors = evaluate(
        truth=args.truth, actual=args.actual, img_file=args.imgfile,
        debug=args.debug, verbose=args.verbose
    )

    print("segmentation_errors", segmentation_errors)
    print("segmentation_ocr_errors", segmentation_ocr_errors)
    print("ocr_errors", ocr_errors)

    if image:
        image.show("errors.png")

    args.truth.close()
    args.actual.close()
