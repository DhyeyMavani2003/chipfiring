"""
Example usage of the dollar game implementation.
This example recreates the graph from Figure 1 in the LaTeX writeup.
"""

from chipfiring.graph import Graph, Vertex
from chipfiring.divisor import Divisor
from chipfiring.dollar_game import DollarGame


def main():
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

    # Add edges (recreating Figure 1)
    G.add_edge(alice, bob)
    G.add_edge(alice, charlie)
    G.add_edge(alice, elise)
    G.add_edge(alice, elise)  # Double edge
    G.add_edge(bob, charlie)
    G.add_edge(charlie, elise)

    # Create initial divisor (wealth distribution)
    initial_divisor = Divisor(G, {
        alice: 2,
        bob: -3,
        charlie: 4,
        elise: -1
    })

    # Create and play the game
    game = DollarGame(G, initial_divisor)
    print("Initial state:")
    print(game)
    print(f"Total money in system: {game.get_degree()}")
    print(f"Is winnable? {game.is_winnable()}")
    print()

    # Try some moves
    print("After Charlie lends:")
    game.fire_vertex(charlie)
    print(game)
    print()

    print("After Bob borrows:")
    game.borrow_vertex(bob)
    print(game)
    print()

    # Try set-firing
    print("After set-firing {Alice, Elise, Charlie}:")
    game.fire_set({alice, elise, charlie})
    print(game)
    print()

    # Check if we've won
    print(f"Is current state effective? {game.is_effective()}")
    print(f"Current wealth distribution: {game.get_current_state()}")


if __name__ == "__main__":
    main() 