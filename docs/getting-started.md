# Getting Started

## Installation

You can install the chipfiring package directly from PyPI:

```bash
pip install chipfiring
```

## Basic Usage

Here's a basic example of how to use the chip-firing game:

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

# Check current state
print(f"Current wealth: {game.get_current_state()}")
print(f"Is effective? {game.is_effective()}")
```

## Visualization

The package includes visualization capabilities using matplotlib:

```python
from chipfiring.visualization import draw_graph, draw_game_state
import matplotlib.pyplot as plt

# Visualize the current state of the game
fig, ax = draw_game_state(game, "Current Game State")
plt.show()  # Show the visualization
```

## Using Dhar's Algorithm

The package includes an implementation of Dhar's algorithm for efficiently determining winnability:

```python
from chipfiring.dhar import is_winnable_dhar, get_winning_strategy_dhar

# Check winnability using Dhar's algorithm
is_winnable = is_winnable_dhar(G, initial_divisor)
print(f"Is winnable? {is_winnable}")

# Get a winning strategy if one exists
strategy = get_winning_strategy_dhar(G, initial_divisor)
if strategy:
    print(f"Winning strategy: {strategy}")
else:
    print("No winning strategy exists")
```

For more examples, check out the [examples directory](https://github.com/DhyeyMavani2003/chipfiring/tree/main/examples) in the repository.
