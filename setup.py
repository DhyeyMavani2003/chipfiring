import os
import re
import setuptools

NAME             = "chipfiring"
AUTHOR           = "Dhyey Mavani"
AUTHOR_EMAIL     = "ddmavani2003@gmail.com"
DESCRIPTION      = "A Python API for visualization and analysis of chip-firing games and related algorithms."
LICENSE          = "MIT"
KEYWORDS         = ""
URL              = "https://github.com/DhyeyMavani2003/" + NAME
README           = "README.md"
CLASSIFIERS      = [
  "Development Status :: 4 - Beta",
  "Intended Audience :: Science/Research",
  "Operating System :: OS Independent",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.8",
  "Programming Language :: Python :: 3.9",
  "Programming Language :: Python :: 3.10",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Programming Language :: Python :: 3.13",
  "Topic :: Scientific/Engineering :: Mathematics",
]
INSTALL_REQUIRES = [
  "numpy",
  "dash",
  "dash-cytoscape",
  "dash-bootstrap-components",
  "networkx",
]
ENTRY_POINTS = {
  
}
SCRIPTS = [
  
]

HERE = os.path.dirname(__file__)

def read(file):
  with open(os.path.join(HERE, file), "r") as fh:
    return fh.read()

VERSION = re.search(
  r'__version__ = [\'"]([^\'"]*)[\'"]',
  read(NAME.replace("-", "_") + "/__init__.py")
).group(1)

LONG_DESCRIPTION = read(README)

if __name__ == "__main__":
  setuptools.setup(
    name=NAME,
    version=VERSION,
    packages=setuptools.find_packages(include=["chipfiring", "chipfiring.*"]),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    license=LICENSE,
    keywords=KEYWORDS,
    url=URL,
    classifiers=CLASSIFIERS,
    install_requires=INSTALL_REQUIRES,
    python_requires=">=3.8",
    entry_points=ENTRY_POINTS,
    scripts=SCRIPTS,
    include_package_data=True    
  )
