from __future__ import annotations

from typing import cast, Tuple  # TODO: Drop `Tuple` after dropping Python 3.8.


RectangleType = Tuple[float, float, float, float]
"""
Custom type for wrapping a simple rectangle.
"""


def intersect(u: RectangleType | None, v: RectangleType | None) -> RectangleType | None:
    """
    Intersection of two rectangles.
    """
    if u is None or v is None:
        return None
    r = (max(u[0], v[0]), max(u[1], v[1]), min(u[2], v[2]), min(u[3], v[3]))
    return r


def area(u: RectangleType | None) -> float:
    """
    Area of a rectangle.
    """
    if u is None:
        return 0
    return max(0, u[2] - u[0]) * max(0, u[3] - u[1])


def overlaps(u: RectangleType | None, v: RectangleType | None) -> bool:
    """
    Predicate: Do the two rectangles overlap?
    """
    return area(intersect(u, v)) > 0


def relative_overlap(u: RectangleType | None, v: RectangleType | None) -> float:
    """
    Relative overlap of the two rectangles, id est overlap in comparison to
    larger rectangle area.
    """
    m = max(area(u), area(v))
    i = area(intersect(u, v))
    return float(i) / m


def mostly_non_overlapping(
        boxes: list[RectangleType | None],
        significant_overlap: float = 0.2
) -> bool:
    """
    Check if the given boxes do not overlap more than the given threshold.
    """
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if relative_overlap(boxes[i], boxes[j]) > significant_overlap:
                return False
    return True


def width(u: RectangleType | None) -> float:
    """
    Width of a rectangle.
    """
    if u is None:
        return 0
    return max(0, u[2] - u[0])


def height(u: RectangleType | None) -> float:
    """
    Height of a rectangle.
    """
    if u is None:
        return 0
    return max(0, u[3] - u[1])


def erode(u: RectangleType | None, tx: float, ty: float) -> RectangleType | None:
    """
    Erode the given rectangle with the given transformation factors.
    """
    if u is None:
        return u

    x = 2 * tx + 1
    y = 2 * ty + 1
    return cast(
        RectangleType,
        tuple([u[0] + x, u[1] + y, u[2] - x, u[3] - y])
    )
