def intersect(u, v):
    """
    Intersection of two rectangles.
    """
    r = (max(u[0], v[0]), max(u[1], v[1]), min(u[2], v[2]), min(u[3], v[3]))
    return r


def area(u):
    """
    Area of a rectangle.
    """
    return max(0, u[2] - u[0]) * max(0, u[3] - u[1])


def overlaps(u, v):
    """
    Predicate: Do the two rectangles overlap?
    """
    return area(intersect(u, v)) > 0


def relative_overlap(u, v):
    m = max(area(u), area(v))
    i = area(intersect(u, v))
    return float(i) / m


def mostly_non_overlapping(boxes, significant_overlap=0.2):
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if relative_overlap(boxes[i], boxes[j]) > significant_overlap:
                return 0
    return 1


def width(u):
    """
    Width of a rectangle.
    """
    return max(0, u[2] - u[0])


def height(u):
    """
    Height of a rectangle.
    """
    return max(0, u[3] - u[1])


def erode(u, tx, ty):
    x = 2 * tx + 1
    y = 2 * ty + 1
    return tuple([u[0] + x, u[1] + y, u[2] - x, u[3] - y])
