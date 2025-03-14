# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../../src/'))
from setuptools_scm import get_version

# -- Project information -----------------------------------------------------
release = get_version(root='../..', relative_to=__file__)

version='.'.join(release.split('.')[:2])
from setuptools_scm import get_version

from comotion import __projectname__  # noqa
from comotion import __author__  # noqa

project = "comotion-sdk"
copyright = '2021, Comotion Business Solutions'
author = "Comotion"

# The full version, including alpha/beta/rc tags.

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
]
extensions.append('sphinx.ext.autodoc')
extensions.append('sphinx.ext.autosummary')
extensions.append('sphinx.ext.intersphinx')
extensions.append('sphinx.ext.mathjax')
extensions.append('sphinx.ext.viewcode')
extensions.append('sphinx.ext.graphviz')

# we use the numpy style
extensions.append('sphinx.ext.napoleon')


# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_material'
html_theme_options = {
    'nav_title': 'Comotion Python SDK',
    'color_primary': 'white',
    'color_accent': 'light-blue',
    'repo_url': 'https://github.com/ComotionLabs/comotion-sdk/',
    'repo_name': 'comotion-sdk',
    'globaltoc_depth': 3
}

html_title = 'Comotion Python SDK Docs'

html_short_title = 'comotion-sdk'

html_favicon = 'favicon.png'

html_logo = 'comotion_logo.png'
suppress_warnings = ["config.cache"]
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']
