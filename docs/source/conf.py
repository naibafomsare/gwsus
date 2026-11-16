# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


import sys
import os
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[2] / "src")
)

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Gwsus'
copyright = '2026, Fabián Peña'
author = 'Fabián Peña'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# extensions = []
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx_gallery.gen_gallery",
    "sphinxcontrib.bibtex",
    "sphinx_pybtex_etal_style",
    "sphinx_copybutton",
]

ROOT = Path(__file__).resolve().parents[2]

sphinx_gallery_conf = {
    "examples_dirs": str(ROOT / "examples"),
    "gallery_dirs": "auto_examples",
    "within_subsection_order": "FileNameSortKey",
    'filename_pattern': r'/example',
    "nested_sections": True,
}

os.environ["SPHINX_BUILD"] = "1"

bibtex_bibfiles = ["biblio.bib"]  # Path to your .bib file relative to conf.py
bibtex_default_style = "unsrt_et_al"


autosummary_generate = True
napoleon_numpy_docstring = True

# Force Sphinx to display members in the order they appear in the source code
autodoc_member_order = 'bysource'

templates_path = ['_templates']
# exclude_patterns = []
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '.ipynb_checkpoints']


autodoc_default_options = {
#    "members": True,
#    "undoc-members": True,
    "special-members": "__post_init__",
    "show-inheritance": True,
}


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'
# html_theme = "sphinx_rtd_theme"
html_theme = "furo"


html_static_path = ['_static']

html_css_files = [
    "custom.css",
]
