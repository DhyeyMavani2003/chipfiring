# chipfiring

> Unified interface for visualization and analysis of chip firing games and related algorithms.

[![Latest Version on PyPI](https://img.shields.io/pypi/v/chipfiring.svg)](https://pypi.python.org/pypi/chipfiring/)
[![Build Status](https://github.com/DhyeyMavani2003/chipfiring/actions/workflows/test.yaml/badge.svg)](https://github.com/DhyeyMavani2003/chipfiring/actions/workflows/test.yaml)
[![Documentation Status](https://readthedocs.org/projects/chipfiring/badge/?version=latest)](https://chipfiring.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/DhyeyMavani2003/chipfiring/badge.svg?branch=main)](https://coveralls.io/github/DhyeyMavani2003/chipfiring?branch=main)
[![Built with PyPi Template](https://img.shields.io/badge/PyPi_Template-v0.8.0-blue.svg)](https://github.com/christophevg/pypi-template)
[![PyPI Downloads](https://static.pepy.tech/badge/chipfiring)](https://pepy.tech/projects/chipfiring)

A Python implementation of the chip-firing game (also known as the dollar game) on graphs. This package provides a mathematical framework for studying and experimenting with chip-firing games, with a focus on the dollar game variant.

## Documentation

Visit [Read the Docs](https://chipfiring.readthedocs.org) for the full
documentation, including overviews and several examples. Repository-specific
guides are available in the [changelog](CHANGELOG.md),
[contributing guide](docs/contributing.md), and
[examples directory](examples/README.md).

## Overview

The chip-firing game is a mathematical model that can be used to study various phenomena in graph theory, algebraic geometry, and other areas of mathematics. In the dollar game variant, we consider a graph where:

- Vertices represent people
- Edges represent relationships between people
- Each vertex has an integer value representing wealth (negative values indicate debt)
- Players can perform lending/borrowing moves by sending money across edges

The goal is to find a sequence of moves that makes everyone debt-free. If such a sequence exists, the game is said to be *winnable*.

## Installation

```bash
pip install chipfiring
```

## Usage

Here is a complete example using the current public API:

```python
from chipfiring import CFDivisor, CFGraph, is_q_reduced, is_winnable, q_reduction

vertices = {"Alice", "Bob", "Charlie", "Elise"}
edges = [
    ("Alice", "Bob", 1),
    ("Alice", "Charlie", 1),
    ("Alice", "Elise", 2),
    ("Bob", "Charlie", 1),
    ("Charlie", "Elise", 1),
]
graph = CFGraph(vertices, edges)
divisor = CFDivisor(
    graph,
    [("Alice", 2), ("Bob", -3), ("Charlie", 4), ("Elise", -1)],
)

print(is_winnable(divisor))

bob_reduced = q_reduction(divisor, q_name="Bob")
print(is_q_reduced(bob_reduced, q_name="Bob"))
```

The predicate and reduction helpers operate on a copy and do not mutate the
supplied divisor. If `q_name` is omitted, reduction preserves the historical
behavior of selecting a minimum-degree vertex.

## Mathematical Background

The implementation follows the mathematical formalization described in the LaTeX writeup, which includes:

1. **Graph Structure**: Finite, connected, undirected multigraphs without loop edges
2. **Divisors**: Elements of the free abelian group on vertices
3. **Laplacian Matrix**: Matrix representation of lending moves
4. **Linear Equivalence**: Equivalence relation on divisors
5. **Effective Divisors**: Divisors with non-negative values
6. **Winnability**: Property of being linearly equivalent to an effective divisor

## Features

- Mathematical graph implementation with support for multigraphs
- Divisor class with operations for lending and borrowing
- Laplacian matrix computations
- Linear equivalence checking
- Set-firing moves
- Winnability and explicit q-reduction
- Baker-Norine rank and graph gonality helpers
- Dhar's burning algorithm and graph orientations
- Interactive graph and divisor visualization
- Type hints and API documentation

## Development

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/DhyeyMavani2003/chipfiring.git
cd chipfiring

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements.docs.txt

# Run the regression tests and package doctests
python -m pytest -q
python -m pytest --doctest-modules chipfiring -q

# Verify the saved-output examples
make check-example-outputs PYTHON=python

# Build documentation
cd docs
make html
```

## License

This project is licensed under the MIT License; see
[LICENSE.txt](https://github.com/DhyeyMavani2003/chipfiring/blob/main/LICENSE.txt).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
