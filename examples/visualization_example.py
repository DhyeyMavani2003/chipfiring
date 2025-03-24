"""
Example demonstrating visualization capabilities of the chip-firing game.
"""

from chipfiring.graph import Graph, Vertex
from chipfiring.divisor import Divisor
from chipfiring.dollar_game import DollarGame
from chipfiring.visualization import draw_game_state
import matplotlib.pyplot as plt


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
    
    # Draw initial state
    fig, ax = draw_game_state(game, "Initial State")
    plt.savefig("initial_state.png")
    plt.close(fig)
    
    # Try some moves and visualize each step
    print("After Charlie lends:")
    game.fire_vertex(charlie)
    fig, ax = draw_game_state(game, "After Charlie Lends")
    plt.savefig("after_charlie_lends.png")
    plt.close(fig)
    
    print("After Bob borrows:")
    game.borrow_vertex(bob)
    fig, ax = draw_game_state(game, "After Bob Borrows")
    plt.savefig("after_bob_borrows.png")
    plt.close(fig)
    
    # Try set-firing
    print("After set-firing {Alice, Elise, Charlie}:")
    game.fire_set({alice, elise, charlie})
    fig, ax = draw_game_state(game, "After Set-Firing {Alice, Elise, Charlie}")
    plt.savefig("after_set_firing.png")
    plt.close(fig)
    
    # Check if we've won
    print(f"Is current state effective? {game.is_effective()}")
    print(f"Current wealth distribution: {game.get_current_state()}")


if __name__ == "__main__":
    main() 