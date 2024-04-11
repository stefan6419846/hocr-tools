Welcome to hocr-tools-lib's documentation!
==========================================

hOCR is a format for representing OCR output, including layout information,
character confidences, bounding boxes, and style information.
It embeds this information invisibly in standard HTML.
By building on standard HTML, it automatically inherits well-defined support
for most scripts, languages, and common layout options.
Furthermore, unlike previous OCR formats, the recognized text and OCR-related
information co-exist in the same file and survives editing and manipulation.
hOCR markup is independent of the presentation.

GitHub: `hocr-tools <https://github.com/stefan6419846/hocr-tools>`_

.. toctree::
   :maxdepth: 1

   cli
   api

About
-----

This repository contains my own fork of the package with quite some changes:

* Allow library usage and reduce code duplicates by this.
* Migrate tests to plain `unittest`-based ones instead of some external framework.
* Remove some deprecated code to make it compatible with latest Python 3 versions.
* Add type hints.

For now, I do not have any direct plans to send a corresponding PR. Unfortunately, as for
quite some similar OCR-related tools, development is rather inactive (at least inside the
official GitHub repositories). Some deprecations have been discussed for a long time, as
well as the library support (which I primarily need), with no real progress.


Installation
------------

You can install this package from PyPI:

.. code:: bash

    python -m pip install hocr-tools-lib

Alternatively, you can use the package from source directly after installing the required dependencies.


Usage
-----

Please refer to the :doc:`cli` or :doc:`api` documentation. Each CLI command has a corresponding file in the ``hocr_tools_lib.tools`` module.


License
-------

This package is subject to the terms of the Apache-2.0 license.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
