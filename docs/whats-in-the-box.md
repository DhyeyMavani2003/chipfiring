# What's in the Box?

The `chipfiring` package provides a comprehensive framework for working with chip-firing games on graphs, with a focus on the dollar game variant. Here's what the package includes:

## Core Components

### Graph Module
- `Graph`: A class representing an undirected multigraph
- `Vertex`: A class representing a vertex in a graph
- `Edge`: A class representing an edge between two vertices

### Divisor Module
- `Divisor`: A class representing a configuration of chips/dollars on the vertices of a graph
- Methods for checking effectiveness, linear equivalence, and principal divisors

### Dollar Game Module
- `DollarGame`: The main game class that manages the chip-firing dynamics
- Methods for firing vertices, borrowing, and checking winnability

## Algorithms

### Dhar's Algorithm
- Functions for efficiently determining winnability of game states
- Implementation of q-reduction for divisors
- Functions for finding legal firing sets

## Visualization

- Tools for visualizing graphs and game states using matplotlib
- Support for custom node/edge colors, positions, and labels

## Examples and Tutorials

The package includes several examples and tutorials:

1. **Basic Dollar Game**: A simple example of setting up and playing the dollar game
2. **Visualization**: Examples of visualizing game states
3. **Dhar's Algorithm**: Demonstrating the use of Dhar's algorithm for winnability

## Mathematical Background

The implementation is based on a rigorous mathematical foundation, including:

- Graph theory concepts (adjacency, Laplacian matrices)
- Divisor theory (linear equivalence)
- Chip-firing dynamics (lending/borrowing moves)

The package aims to be useful both for educational purposes and for research in algebraic graph theory and related areas.
