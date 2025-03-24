#!/usr/bin/env python3
"""
Example demonstrating the use of Dhar's algorithm for the chip-firing game.
"""

from chipfiring.graph import Graph, Vertex
from chipfiring.divisor import Divisor
from chipfiring.dollar_game import DollarGame
from chipfiring.dhar import is_winnable_dhar
from chipfiring.visualization import draw_game_state
import matplotlib.pyplot as plt


def main():
    print("Example demonstrating Dhar's algorithm for the chip-firing game.")
    print("=" * 70)
    
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

    # Create and initialize the game
    game = DollarGame(G, initial_divisor)
    
    print("\nInitial State:")
    print(game)
    print(f"Total money in system: {game.get_degree()}")
    print(f"Is winnable? {game.is_winnable()}")
    
    # Visualize initial state
    fig, ax = draw_game_state(game, "Initial State")
    plt.show()
    
    # Set Bob as our distinguished vertex q
    q = bob
    print(f"\nUsing {q} as the distinguished vertex for q-reduction")
    
    # Step 1: Find a legal firing set using Dhar's algorithm
    print("\nStep 1: Finding a legal firing set using Dhar's algorithm...")
    legal_set = game.find_legal_firing_set(q)
    
    print(f"Legal firing set: {legal_set}")
    
    # Step 2: Apply q-reduction
    print("\nStep 2: Computing the q-reduced divisor...")
    q_reduced = game.compute_q_reduced_divisor(q)
    
    print(f"q-reduced divisor: {q_reduced}")
    
    # Create a game state with the q-reduced divisor
    q_reduced_game = DollarGame(G, q_reduced)
    
    # Visualize q-reduced state
    fig, ax = draw_game_state(q_reduced_game, "q-reduced State")
    plt.show()
    
    # Check winnability
    print(f"\nIs winnable using Dhar's algorithm? {is_winnable_dhar(G, initial_divisor)}")
    
    # Get a winning strategy
    print("\nComputing a winning strategy...")
    strategy = game.get_winning_strategy()
    
    if strategy:
        print(f"Winning strategy found: {strategy}")
        
        # Apply the strategy
        print("\nApplying the winning strategy...")
        for v in strategy:
            game.borrow_vertex(v)
            print(f"After borrowing at {v}: {game.get_current_state()}")
        
        # Check final state
        print(f"\nFinal state is effective? {game.is_effective()}")
        
        # Visualize final state
        fig, ax = draw_game_state(game, "Final State After Strategy")
        plt.show()
    else:
        print("No winning strategy found.")


if __name__ == "__main__":
    main() 