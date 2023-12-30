from __future__ import annotations

import re
from typing import cast

from lxml.html import HtmlElement

from hocr_tools_lib.utils.rectangle_utils import RectangleType


def get_prop(node: HtmlElement, name: str, strip_value: bool = False) -> str | None:
    title = node.get('title')
    if not title:
        return None
    props = title.split(';')
    for prop in props:
        key, args = prop.split(None, 1)
        if strip_value:
            args = args.strip('"')
        if key == name:
            return cast(str, args)
    return None


def get_bbox(node: HtmlElement) -> RectangleType | None:
    bbox = get_prop(node, 'bbox')
    if not bbox:
        return None
    return cast(
        RectangleType,
        tuple([int(x) for x in bbox.split()])
    )


def get_text(node: HtmlElement) -> str:
    text_nodes = node.xpath(".//text()")
    s = "".join([text for text in text_nodes])
    return re.sub(r'\s+', ' ', s)
