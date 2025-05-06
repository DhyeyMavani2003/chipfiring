# Chip-Firing Game

> A Python implementation of the chip-firing game (also known as the dollar game) on graphs, with a focus on mathematical algorithms and visualizations.

[![Latest Version on PyPI](https://img.shields.io/pypi/v/chipfiring.svg)](https://pypi.python.org/pypi/chipfiring/)
![Build Status](https://github.com/DhyeyMavani2003/chipfiring/actions/workflows/test.yaml/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/chipfiring/badge/?version=latest)](https://chipfiring.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/DhyeyMavani2003/chipfiring/badge.svg?branch=main)](https://coveralls.io/github/DhyeyMavani2003/chipfiring?branch=main)
[![Built with PyPi Template](https://img.shields.io/badge/PyPi_Template-v0.8.0-blue.svg)](https://github.com/christophevg/pypi-template)

## Overview

The chip-firing game is a mathematical model that can be used to study various phenomena in graph theory, algebraic geometry, and other areas of mathematics. In the dollar game variant, we consider a graph where:

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

```bash
pip install chipfiring
```

## Quick Example

```python
from chipfiring import Graph, Vertex, Divisor, DollarGame

# Create vertices and graph
alice = Vertex("Alice")
bob = Vertex("Bob")
charlie = Vertex("Charlie")

G = Graph()
G.add_vertex(alice)
G.add_vertex(bob)
G.add_vertex(charlie)

G.add_edge(alice, bob)
G.add_edge(bob, charlie)
G.add_edge(charlie, alice)

# Create initial wealth distribution
D = Divisor(G, {alice: 2, bob: -1, charlie: -1})

# Create and play the game
game = DollarGame(G, D)
print(f"Is winnable? {game.is_winnable()}")
```

## Contents

```{toctree}
:maxdepth: 2
:caption: Documentation

whats-in-the-box.md
getting-started.md
contributing.md
api/index
```

## API Documentation

The complete API documentation for the chipfiring package can be found in the [API Documentation](api/index) section.