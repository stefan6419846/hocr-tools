# Copyright 2013 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Create a searchable PDF from a pile of hOCr + JPEG. Tested with
Tesseract.
"""

from __future__ import annotations

import argparse
import base64
import glob
import io
import os
import re
import sys
import zlib
from typing import Any

try:
    from bidi import get_display  # type: ignore[import-untyped]
except ImportError:
    # For version < 0.5.
    from bidi.algorithm import get_display  # type: ignore[import-untyped]
from reportlab.pdfbase import pdfmetrics  # type: ignore[import-untyped]
from reportlab.pdfbase.ttfonts import TTFont  # type: ignore[import-untyped]
from reportlab.pdfgen.canvas import Canvas  # type: ignore[import-untyped]

from lxml import etree, html
from PIL import Image


class StdoutWrapper:
    """
    Wrapper around stdout that ensures 'bytes' data is decoded
    to 'latin1' (0x00 - 0xff) before writing out. This is necessary for
    the invisible font to be injected as bytes, but written out as a string.
    """

    def write(self, data: str | bytes, *args: Any, **kwargs: Any) -> None:
        if isinstance(data, bytes):
            data = data.decode('latin1')
        sys.stdout.write(data)


class NoImagesFoundError(RuntimeError):
    """
    Custom error class when no images could be found.
    """
    pass


def export_pdf(directory: str, default_dpi: int = 300, savefile: str | None = None) -> None:
    """
    Create a searchable PDF from a pile of HOCR + JPEG.

    :param directory: The input directory to use.
    :param default_dpi: The image resolution to use.
    :param savefile: If set, save the PDF file to this file instead of
                     displaying it on stdout.
    """
    images = sorted(glob.glob(os.path.join(directory, '*.jpg')))
    if len(images) == 0:
        raise NoImagesFoundError(
            f"WARNING: No JPG images found in the folder {directory}"
            "\nScript cannot proceed without them and will terminate now.\n"
        )
    load_invisible_font()
    pdf = Canvas(savefile if savefile else StdoutWrapper(), pageCompression=1)
    pdf.setCreator('hocr-tools')
    pdf.setTitle(os.path.basename(directory))
    dpi = default_dpi
    for image in images:
        im = Image.open(image)
        w, h = im.size
        try:
            dpi = im.info['dpi'][0]
        except KeyError:
            pass
        width = w * 72 / dpi
        height = h * 72 / dpi
        pdf.setPageSize((width, height))
        pdf.drawImage(image, 0, 0, width=width, height=height)
        add_text_layer(pdf, image, height, dpi)
        pdf.showPage()
        im.close()
    pdf.save()


def add_text_layer(pdf: Canvas, image: str, height: float, dpi: int) -> None:
    """
    Draw an invisible text layer for OCR data.

    :param pdf: The PDF canvas to add the layer to.
    :param image: The image path to determine the hOCR file from.
    :param height: The page height to use for positioning/scaling.
    :param dpi: The resolution to use for positioning/scaling.
    """
    p1 = re.compile(r'bbox((\s+\d+){4})')
    p2 = re.compile(r'baseline((\s+[\d\.\-]+){2})')
    hocr_file = os.path.splitext(image)[0] + ".hocr"
    hocr = etree.parse(hocr_file, html.XHTMLParser())
    for line in hocr.xpath('//*[@class="ocr_line"]'):
        line_box_match = p1.search(line.attrib['title'])
        assert line_box_match is not None
        line_box_str = line_box_match.group(1).split()
        line_box: list[float] = [float(i) for i in line_box_str]
        try:
            baseline_match = p2.search(line.attrib['title'])
            assert baseline_match is not None
            baseline_str = baseline_match.group(1).split()
            baseline: list[float] = [float(i) for i in baseline_str]
        except AttributeError:
            baseline = [0, 0]
        xpath_elements = './/*[@class="ocrx_word"]'
        if not (line.xpath('boolean(' + xpath_elements + ')')):
            # If there are no words elements present, we switch to lines
            # as elements.
            xpath_elements = '.'
        for word in line.xpath(xpath_elements):
            rawtext = word.text_content().strip()
            if rawtext == '':
                continue
            font_width = pdf.stringWidth(rawtext, 'invisible', 8)
            if font_width <= 0:
                continue
            box_match = p1.search(word.attrib['title'])
            assert box_match is not None
            box_str = box_match.group(1).split()
            box: list[float] = [float(i) for i in box_str]
            b = polyval(
                baseline,
                (box[0] + box[2]) / 2 - line_box[0]
            ) + line_box[3]
            text = pdf.beginText()
            text.setTextRenderMode(3)  # Double invisible.
            text.setFont('invisible', 8)
            text.setTextOrigin(box[0] * 72 / dpi, height - b * 72 / dpi)
            box_width = (box[2] - box[0]) * 72 / dpi
            text.setHorizScale(100.0 * box_width / font_width)
            rawtext = get_display(rawtext)
            text.textLine(rawtext)
            pdf.drawText(text)


def polyval(poly: list[float], x: float) -> float:
    return x * poly[0] + poly[1]


def load_invisible_font() -> None:
    """
    Load the invisible font to use for rendering into `reportlab`.
    """
    # This is a variant of the Mienai font as provided by Fredrick R. Brennan
    # at https://github.com/MFEK/Mienai.ttf
    # It has been edited with FontForge to explicitly set the PS font name.
    #
    # The original and the modified file are subject to the terms of the
    # CC0-1.0 license. For further information, either visit the GitHub URL
    # above or go to https://creativecommons.org/publicdomain/zero/1.0/
    font = b"""
eJztVc9rXFUU/u59b95MkmJSAzWkcfr60CiVpDMvJcZQQfJjrJRBa0PqIpAMcTIzmJk3TGIZV7pw
4cJFKa5c+GMhEpC6EVFQcCFKs1CLWIuQTpiVCxdBWlvMMPG7795kJoH8A+oZ7j3fOe9+5553z5t7
IAB04w1YKKdSM+kPH/phFogN0Dvw7NR0Co+hD4g2aLvPXzzt19eu/g6IKu3ZxWKmPHEj3aS9Cdhn
c5mV8s4OIyF6h89jueXXlhCK87ia89nMy+78c08SqnijeTo6H5Zz5J+h/Ui+uFp1w/XiJ049y8Fi
xvBVPp3FTLVsLyLJ5y+pfEqZYvbbL8uDOr54uxysrAbp+sfc/zM+f/oy4zdSAzZTGVPxL4fxe33a
cyo+1Ltz3Heqf8x3n72Lrli4W83belPperz3c7QkBmkQOR23/r6EyRhann1ihx57z5bc7TQm6Dqy
y4hBXEEEsci7kRGax7W2bmBJPoi9rYAPID99AdXtXTudmj6PZwg6Ij83L4gRq2J3L0C8X7unk9w/
KJYZAzpLa5SWCG3b6qceg8tM+/A6dkRSXBRVcVV+Lzesd6w16xt30E244+6U+8lJz3O8o17ce8I7
52UfXd+M39/Zlqx3mCSZL4bM7+Qtw+wl8ynDlF631x8yFwxTaGbzR463miWFG8uNSw2+WY3Vr31V
m7l9W7/Axi8bXwC/jZ6oR3XFxsQo1Z/hMW5pTfQXT63fHPcxGZdeiAaN55Q5hXax9up2sH4H5SDz
f/mXi3BaRbfMPbFP/ntfxAO41nYK0mABB0cNlrxHPIMtoqLBNte8Z3AEXfjaYIe/X9W/0O4wUTUW
OEKkseQ11mewhSn2I41trrlicATH8JHBDv3XVag0CsiihAw10oVsKUM9gYC/VwiCgHOKRgmroa4g
x/UufAwjQT3O0R5De5K8LocwwuFzlQ82rlRQWk0FlVzW9YfVXan3IkiODY0M+Qn/zCHJzNJVwQpd
KgsVW+2M2WxlpRCU3ORw4hBiqznoChwU9h0hIYUVfbVUSFA62YrLeYV8w+Htqyuo+lEPT1hqXqhb
33s4126uHw91e18UPWzibOOTbZ1mfyZ2DM6SHmqFs/QPxKbPLw==
"""
    uncompressed = bytearray(zlib.decompress(base64.b64decode(font)))
    ttf = io.BytesIO(uncompressed)
    ttf.name = '(invisible.ttf)'
    pdfmetrics.registerFont(TTFont('invisible', ttf))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a searchable PDF from a pile of hOCR and JPEG"
    )
    parser.add_argument(
        "imgdir",
        help=(
            "directory with the hOCR and JPEG files (corresponding "
            "JPEG and hOCR files have to have the same name with "
            "their respective file ending)"
        )
    )
    parser.add_argument(
        "--savefile",
        help="Save to this file instead of outputting to stdout"
    )
    args = parser.parse_args()
    if not os.path.isdir(args.imgdir):
        sys.exit(f"ERROR: Given path '{args.imgdir}' is not a directory")
    export_pdf(directory=args.imgdir, default_dpi=300, savefile=args.savefile)
