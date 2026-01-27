# Development Version

* Allow setting the maximum image pixel size for *Pillow* in `hocr_pdf`.
* Drop support for Python <= 3.9.
* Avoid using deprecated `argparse.FileType`.

# Version 1.2.0 - 2025-07-01

* Gracefully handle hOCR files from `kraken` in `hocr_pdf`.
* Deal with non-integer widths and heights in `hocr_pdf` which would previously lead to some white borders.
* Fix handling of accented characters in `hocr_pdf` due to a change in `reportlab>=4.0.9`.
* Remove the stdout output option for `hocr_pdf` due to unexpected behavior.
* Remove unused and untested `hocr_extract_g1000` tool.
* Drop support for Python < 3.9.

# Version 1.1.0 - 2024-07-23

* Fix deprecation warning from `lxml` in `hocr_wordfreq`.
* Ensure compatibility with `python-bidi>=0.5`, while keeping support for older versions.
* Migrate from `setup.py` to `pyproject.toml`.
* Add Read the Docs configuration and missing docs.

# Version 1.0.3 - 2024-03-18

* Add type hints.
* Fix `hocr_pdf` for `reportlab>=4.1.0`, which would not render the text anymore.

# Version 1.0.2 - 2023-12-29

* Fix installation instructions.

# Version 1.0.1 - 2023-12-29

* Fix rendering on PyPI.

# Version 1.0.0 - 2023-12-29

* First public release.
