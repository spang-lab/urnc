# Configuration file for the Sphinx documentation builder.
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html.

# Project Info
project = 'urnc'
copyright = '2023, Michael Huttner, Tobias Schmidt'
author = 'Michael Huttner, Tobias Schmidt'
release = '1.6.3'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'myst_parser', # markdown support
    'sphinx.ext.autodoc',
    'sphinx.ext.duration', # print sphinx runtime
    'sphinx_rtd_theme' # read the docs theme
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files. This pattern also affects
# html_static_path and html_extra_path.
exclude_patterns = []

# The theme to use for HTML and HTML Help pages. See the documentation for a
# list of builtin themes.
html_theme = "sphinx_rtd_theme"

# https://sphinx-rtd-theme.readthedocs.io/en/stable/configuring.html#theme-options
html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files, so
# a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
