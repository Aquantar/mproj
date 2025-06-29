# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))  # macht dein Projekt im Hauptverzeichnis auffindbar

# Import necessary modules for custom role
from docutils import nodes
from docutils.parsers.rst import roles

project = 'Jopp_PJS'
copyright = '2025, Serdar Isik, Johannes Klauer'
author = 'Serdar Isik, Johannes Klauer'
release = '16.05.2025'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',          # Für Google/NumPy-Stil-Dokumentation
    'sphinx_autodoc_typehints',     # Optional, falls du Type Hints nutzt
    'sphinx_rtd_theme', # Ensure this is present if you are using the theme
]

templates_path = ['_templates']
exclude_patterns = []

language = 'English'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

html_css_files = [
    'custom.css', # Your new custom CSS file
]

html_context = {
    "display_github": True,
    "github_user": "your-github-username",
    "github_repo": "your-repo-name",
    "github_version": "main",
    "conf_py_path": "/docs/",
}

# -- Custom roles setup -----------------------------------------------------
# This function is called by Sphinx to set up extensions and custom configurations.
def setup(app):
    # This is a more direct way to register an inline role that applies a CSS class.
    # It avoids potential compatibility issues with add_generic_role or add_inline_css_class
    # for older/specific Sphinx/Docutils versions.
    app.add_role(
        'varname',
        # The role function: `typ, rawtext, text, lineno, inliner, options={}, content=[]`
        # returns (nodes, messages)
        lambda typ, rawtext, text, lineno, inliner, options={}, content=[]: (
            [nodes.inline(rawtext, text, classes=['varname'])], []
        )
    )