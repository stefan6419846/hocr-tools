# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# Project information
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from importlib.metadata import version as _version


project = "hocr-tools-lib"
copyright = "2024, Thomas Breuel, stefan6419846"
author = "Thomas Breuel, stefan6419846"
release = _version("hocr-tools-lib")

# General configuration
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc", "sphinx.ext.intersphinx"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

nitpicky = True


# Options for HTML output
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

master_doc = "index"
html_theme = "furo"
html_static_path = ["_static"]


# Options for cross-referencing.

autoclass_content = "both"
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "lxml": ("https://lxml.de/apidoc/", None),
    "PIL": ("https://pillow.readthedocs.io/en/stable", None),
    "reportlab": ("https://reportlab-docs-inofficial.readthedocs.io/en/stable", None),
}
