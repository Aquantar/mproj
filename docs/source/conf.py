# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))  # macht dein Projekt im Hauptverzeichnis auffindbar






project = 'Jopp_PJS'
copyright = '2025, Serdar Isik, Johannes Klauer'
author = 'Serdar Isik, Johannes Klauer'
release = '16.05.2025'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',        # Für Google/NumPy-Stil-Dokumentation
    'sphinx_autodoc_typehints',   # Optional, falls du Type Hints nutzt
]

templates_path = ['_templates']
exclude_patterns = []

language = 'English'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
