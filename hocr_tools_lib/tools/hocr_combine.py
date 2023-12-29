import argparse

from lxml import etree, html


def combine(filenames):
    doc = html.parse(filenames[0])
    pages = doc.xpath("//*[@class='ocr_page']")
    container = pages[-1].getparent()

    for filename in filenames[1:]:
        doc2 = html.parse(filename)
        pages = doc2.xpath("//*[@class='ocr_page']")
        for page in pages:
            container.append(page)

    return etree.tostring(doc, pretty_print=True).decode('UTF-8')


def main():
    parser = argparse.ArgumentParser(
        description="combine multiple hOCR documents into one"
    )
    parser.add_argument(
        "filenames", help="hOCR files", nargs='+'
    )
    args = parser.parse_args()

    combined = combine(args.filenames)
    print(combined)
