# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


import sys
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
]

ROOT = Path(__file__).resolve().parents[2]

sphinx_gallery_conf = {
    "examples_dirs": str(ROOT / "examples"),
    "gallery_dirs": "auto_examples",
}


autosummary_generate = True
napoleon_numpy_docstring = True

# Force Sphinx to display members in the order they appear in the source code
autodoc_member_order = 'bysource'

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'
# html_theme = "sphinx_rtd_theme"
html_theme = "furo"

# html_theme_options = {
#    "light_logo": "logo-light.png",
#    "dark_logo": "logo-dark.png",
#    "sidebar_hide_name": False,
#    "navigation_with_keys": True,
#    "announcement": "📢 New release: 2.0.0 is out!",
# }


html_static_path = ['_static']
