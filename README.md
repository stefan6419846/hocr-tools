# hocr-tools

## About

hOCR is a format for representing OCR output, including layout information,
character confidences, bounding boxes, and style information.
It embeds this information invisibly in standard HTML.
By building on standard HTML, it automatically inherits well-defined support
for most scripts, languages, and common layout options.
Furthermore, unlike previous OCR formats, the recognized text and OCR-related
information co-exist in the same file and survives editing and manipulation.
hOCR markup is independent of the presentation.

There is a [Public Specification](http://kba.github.io/hocr-spec/1.2/) for the hOCR Format.

### About this fork

This repository contains my own fork of the package with quite some changes:

* Allow library usage and reduce code duplicates by this.
* Migrate tests to plain *unittest*-based ones instead of some external framework.
* Remove some deprecated code to make it compatible with latest Python 3 versions.

For now, I do not have any direct plans to send a corresponding PR. Unfortunately, as for
quite some similar OCR-related tools, development is rather inactive (at least inside the
official GitHub repositories). Some deprecations have been discussed for a long time, as
well as the library support (which I primarily need), with no real progress.

## Installation

You can install hocr-tools along with its dependencies from
[PyPI](https://pypi.python.org/pypi/hocr-tools-lib):

```sh
pip install hocr-tools-lib
```

Or from the Git checkout:

```
pip install .
```

## Available Programs

Included command line programs:

### hocr-check

```
hocr-check file.html
```

Perform consistency checks on the hOCR file.

### hocr-combine

```
hocr-combine file1.html [file2.html ...]
```

Combine the OCR pages contained in each HTML file into a single document.
The document metadata is taken from the first file.

### hocr-cut

```
hocr-cut [-h] [-d] [file.html]
```

Cut a page (horizontally) into two pages in the middle
such that the most of the bounding boxes are separated
nicely, e.g. cutting double pages or double columns

### hocr-eval-lines

```
hocr-eval-lines [-v] true-lines.txt hocr-actual.html
```

Evaluate hOCR output against ASCII ground truth.  This evaluation method
requires that the line breaks in true-lines.txt and the ocr_line elements
in hocr-actual.html agree (most ASCII output from OCR systems satisfies this
requirement).

### hocr-eval-geom

```
hocr-eval-geom [-e element-name] [-o overlap-threshold] hocr-truth hocr-actual
```

Compare the segmentations at the level of the element name (default: ocr_line).
Computes undersegmentation, oversegmentation, and missegmentation.

### hocr-eval

```
hocr-eval hocr-true.html hocr-actual.html
```

Evaluate the actual OCR with respect to the ground truth.  This outputs
the number of OCR errors due to incorrect segmentation and the number
of OCR errors due to character recognition errors.

It works by aligning segmentation components geometrically, and for each
segmentation component that can be aligned, computing the string edit distance
of the text the segmentation component contains.

### hocr-extract-g1000

Extract lines from [Google 1000 book sample](http://commondatastorage.googleapis.com/books/icdar2007/README.txt)

### hocr-extract-images

```
hocr-extract-images [-b BASENAME] [-p PATTERN] [-e ELEMENT] [-P PADDING] [file]
```

Extract the images and texts within all the ocr_line elements within the hOCR file.
The `BASENAME` is the image directory, the default pattern is `line-%03d.png`,
the default element is `ocr_line` and there is no extra padding by default.

### hocr-lines

```
hocr-lines [FILE]
```

Extract the text within all the ocr_line elements within the hOCR file
given by FILE. If called without any file, `hocr-lines` reads
hOCR data from stdin.

### hocr-merge-dc

```
hocr-merge-dc dc.xml hocr.html > hocr-new.html
```

Merges the Dublin Core metadata into the hOCR file by encoding the data in its header.

### hocr-pdf

```
hocr-pdf <imgdir> > out.pdf
hocr-pdf --savefile out.pdf <imgdir>
```

Create a searchable PDF from a pile of hOCR and JPEG. It is important that the corresponding JPEG and hOCR files have the same name with their respective file ending. All of these files should lie in one directory, which one has to specify as an argument when calling the command, e.g. use `hocr-pdf . > out.pdf` to run the command in the current directory and save the output as `out.pdf` alternatively `hocr-pdf . --savefile out.pdf` which avoids routing the output through the terminal.

### hocr-split

```
hocr-split file.html pattern
```

Split a multipage hOCR file into hOCR files containing one page each.
The pattern should something like "base-%03d.html"

### hocr-wordfreq

```
hocr-wordfreq [-h] [-i] [-n MAX] [-s] [-y] [file.html]
```

Outputs a list of the most frequent words in an hOCR file with their number of occurrences.
If called without any file, `hocr-wordfreq` reads hOCR data (for example from `hocr-combine`) from stdin.

By default, the first 10 words are shown, but any number can be requested with `-n`.
Use `-i` to ignore upper and lower case, `-s` to split on spaces only which will then
lead to words also containing punctations, and `-y` tries to dehyphenate the text
(separation of words at line break with a hyphen) before analysis.


