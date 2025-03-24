# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

project = u'chipfiring'
copyright = u'2025-2025, Dhyey Dharmendrakumar Mavani'
author = u'Dhyey Dharmendrakumar Mavani'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "autodoc2",
    "sphinx.ext.linkcode",
    "sphinx_rtd_theme",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

autodoc2_render_plugin = "myst"

# Configure autodoc2 to find the chipfiring package
sys.path.insert(0, os.path.abspath('..'))

autodoc2_packages = [
  {
    "path": "../chipfiring",
    "exclude_dirs": [],
    "auto_mode": True
  }
]

# Make sure the api docs are included in the toctree
autodoc2_index_template = """
# API Reference

{% for obj in documentables %}
{% if obj.is_package %}
```{toctree}
:maxdepth: 1
:titlesonly:
{% for document in obj.documents %}
{{ document.full_qualname }}
{% endfor %}
```
{% endif %}
{% endfor %}
"""

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'

html_static_path = ["_static"]

# -- Options for LaTeX output ------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-latex-output
latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '10pt',
}

latex_documents = [
    (
        'index',
        'chipfiring.tex',
        'chipfiring Documentation',
        author,
        'manual'
    ),
]

# Add source code link configuration
def linkcode_resolve(domain, info):
    if domain != 'py':
        return None
    if not info['module']:
        return None
    filename = info['module'].replace('.', '/')
    return f"https://github.com/DhyeyMavani2003/chipfiring/blob/master/{filename}.py"