import argparse
import re

from lxml import etree, html

from hocr_tools_lib.utils.node_utils import get_text


DC_KNOWN = [
    "dc:title", "dc:creator", "dc:subject", "dc:description", "dc:publisher",
    "dc:contributor", "dc:date", "dc:type", "dc:format", "dc:identifier",
    "dc:source", "dc:language", "dc:relation", "dc:coverage", "dc:rights"
]


def merge_dc(dc, hocr):
    dc_doc = etree.parse(dc, html.XHTMLParser())
    hocr_doc = html.parse(hocr)

    # Remove all existing META tags representing Dublin Core metadata.
    hocr_meta = hocr_doc.xpath("//HEAD|//head")
    assert hocr_meta != []
    hocr_meta = hocr_meta[0]

    hocr_nodes = hocr_doc.xpath("//head//meta[starts-with(@name,'DC.')]")
    for node in hocr_nodes:
        node.getparent().remove(node)

    # Find all the Dublin Core tags in the Dublin Core metadata.
    dc_nodes = dc_doc.xpath(
        "//dc:*", namespaces={"dc": "http://purl.org/dc/elements/1.1/"}
    )
    for node in dc_nodes:
        node_tag = re.sub(
            r'^{http://purl.org/dc/elements/1.1/}', 'dc:', node.tag
        )
        if node_tag in DC_KNOWN:
            name = re.sub(r'^dc:', 'DC.', node_tag)
            value = get_text(node)
            value = re.sub("[\t\r\n'\"]", " ", value).strip()
            value = value[:500]
            hnode = etree.Element(
                "meta", nsmap={'DC': 'http://purl.org/dc/elements/1.1'}
            )
            hnode.attrib['name'] = name
            hnode.attrib['content'] = value
            hocr_meta.append(hnode)

    return etree.tostring(hocr_doc, pretty_print=True)


def main():
    parser = argparse.ArgumentParser(
        description="merge Dublin Core metadata into hOCR header files"
    )
    parser.add_argument(
        "dc",
        help="XML file with Dublin Core metadata",
        type=argparse.FileType('r')
    )
    parser.add_argument("hocr", help="hOCR file", type=argparse.FileType('r'))
    args = parser.parse_args()

    merged = merge_dc(dc=args.dc, hocr=args.hocr)
    print(merged)

    args.dc.close()
    args.hocr.close()
