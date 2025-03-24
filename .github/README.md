# chipfiring

> Unified interface for visualization and analysis of chip firing games and related algorithms.

[![Latest Version on PyPI](https://img.shields.io/pypi/v/chipfiring.svg)](https://pypi.python.org/pypi/chipfiring/)
[![Build Status](https://github.com/DhyeyMavani2003/chipfiring/actions/workflows/test.yaml/badge.svg)](https://github.com/DhyeyMavani2003/chipfiring/actions/workflows/test.yaml)
[![Documentation Status](https://readthedocs.org/projects/chipfiring/badge/?version=latest)](https://chipfiring.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/DhyeyMavani2003/chipfiring/badge.svg)](https://coveralls.io/github/DhyeyMavani2003/chipfiring?branch=master)
[![Built with PyPi Template](https://img.shields.io/badge/PyPi_Template-v0.8.0-blue.svg)](https://github.com/christophevg/pypi-template)

A Python implementation of the chip-firing game (also known as the dollar game) on graphs. This package provides a mathematical framework for studying and experimenting with chip-firing games, with a focus on the dollar game variant.

## Documentation

Visit [Read the Docs](https://chipfiring.readthedocs.org) for the full documentation, including overviews and several examples.

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

Here's a simple example of how to use the package:

```python
from chipfiring.graph import Graph, Vertex
from chipfiring.divisor import Divisor
from chipfiring.dollar_game import DollarGame

# Create vertices
alice = Vertex("Alice")
bob = Vertex("Bob")
charlie = Vertex("Charlie")
elise = Vertex("Elise")

# Create graph
G = Graph()
G.add_vertex(alice)
G.add_vertex(bob)
G.add_vertex(charlie)
G.add_vertex(elise)

# Add edges
G.add_edge(alice, bob)
G.add_edge(alice, charlie)
G.add_edge(alice, elise)
G.add_edge(bob, charlie)
G.add_edge(charlie, elise)

# Create initial wealth distribution
initial_divisor = Divisor(G, {
    alice: 2,
    bob: -3,
    charlie: 4,
    elise: -1
})

# Create and play the game
game = DollarGame(G, initial_divisor)

# Check if game is winnable
print(f"Is winnable? {game.is_winnable()}")

# Try some moves
game.fire_vertex(charlie)  # Charlie lends
game.borrow_vertex(bob)    # Bob borrows
game.fire_set({alice, elise, charlie})  # Set-firing move

# Check current state
print(f"Current wealth: {game.get_current_state()}")
print(f"Is effective? {game.is_effective()}")
```

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
- Comprehensive type hints and documentation

## Development

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/yourusername/chipfiring.git
cd chipfiring

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements.docs.txt

# Run tests
pytest

# Build documentation
cd docs
make html
```

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE.txt) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
