import re


def get_prop(node, name, strip_value=False):
    title = node.get('title')
    if not title:
        return None
    props = title.split(';')
    for prop in props:
        key, args = prop.split(None, 1)
        if strip_value:
            args = args.strip('"')
        if key == name:
            return args
    return None


def get_bbox(node):
    bbox = get_prop(node, 'bbox')
    if not bbox:
        return None
    return tuple([int(x) for x in bbox.split()])


def get_text(node):
    text_nodes = node.xpath(".//text()")
    s = "".join([text for text in text_nodes])
    return re.sub(r'\s+', ' ', s)
