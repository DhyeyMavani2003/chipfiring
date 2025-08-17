# Chip-Firing Game

> A Python package for the chip-firing games (i.e. the dollar game, the gonality game, etc.) on graphs, with a focus on mathematical properties and algorithms.

[![Latest Version on PyPI](https://img.shields.io/pypi/v/chipfiring.svg)](https://pypi.python.org/pypi/chipfiring/)
![Build Status](https://github.com/DhyeyMavani2003/chipfiring/actions/workflows/test.yaml/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/chipfiring/badge/?version=latest)](https://chipfiring.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/DhyeyMavani2003/chipfiring/badge.svg?branch=main)](https://coveralls.io/github/DhyeyMavani2003/chipfiring?branch=main)
[![Built with PyPi Template](https://img.shields.io/badge/PyPi_Template-v0.8.0-blue.svg)](https://github.com/christophevg/pypi-template)
[![PyPI Downloads](https://static.pepy.tech/badge/chipfiring)](https://pepy.tech/projects/chipfiring)

## Overview

The chip-firing game is a mathematical model that can be used to study various phenomena in graph theory, algebraic geometry, and other areas of mathematics. 

In the dollar game variant, we consider a graph where:

- Vertices represent people
- Edges represent relationships between people
- Each vertex has an integer value representing wealth (negative values indicate debt)
- Players can perform lending/borrowing moves by sending money across edges

The goal is to find a sequence of moves that makes everyone debt-free. If such a sequence exists, the game is said to be *winnable*.

## Features

- Mathematical graph implementation with support for multigraphs
- Divisor class with operations for lending and borrowing
- Laplacian matrix computations
- Linear equivalence checking
- Set-firing moves
- Dhar's algorithm for efficient winnability determination
- Visualization tools for graphs and game states
- Comprehensive type hints and documentation

## Installation

You can install the chipfiring package directly from PyPI using pip:

```bash
pip install chipfiring
```

Note: the most up-to-date version of the package can be found at https://pypi.org/project/chipfiring/.

## Contents

```{toctree}
:maxdepth: 2
:caption: Documentation

contributing.md
api/index.rst
```

## API Documentation

The complete API documentation for the chipfiring package can be found in the [API Documentation](api/index) section.

## Basic Usage

Usage guidelines are included within the API documentation. For more examples and full-analysis workflows, check out the [examples directory](https://github.com/DhyeyMavani2003/chipfiring/tree/main/examples) in the GitHubrepository.
