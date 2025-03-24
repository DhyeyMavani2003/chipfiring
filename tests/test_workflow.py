"""
Tests for the complete workflow of the chip-firing game.
"""

import pytest
from chipfiring.graph import Graph, Vertex
from chipfiring.divisor import Divisor
from chipfiring.dollar_game import DollarGame


@pytest.fixture
def example_setup():
    """Create an example setup for testing."""
    # Create vertices
    v1 = Vertex("A")
    v2 = Vertex("B")
    v3 = Vertex("C")
    v4 = Vertex("E")

    # Create graph
    G = Graph()
    G.add_vertex(v1)
    G.add_vertex(v2)
    G.add_vertex(v3)
    G.add_vertex(v4)

    # Add edges
    G.add_edge(v1, v2)
    G.add_edge(v1, v3)
    G.add_edge(v1, v4)
    G.add_edge(v1, v4)  # Double edge
    G.add_edge(v2, v3)
    G.add_edge(v3, v4)

    # Create divisor
    D = Divisor(G, {v1: 2, v2: -3, v3: 4, v4: -1})

    return G, D, v2


def test_example_workflow(example_setup):
    """Test the complete example workflow."""
    G, D, q = example_setup

    # Create a DollarGame instance
    game = DollarGame(G, D)

    # Test initial state
    assert game.get_degree() == 2  # 2 + (-3) + 4 + (-1) = 2
    assert not game.is_effective()  # Some vertices have negative values

    # Test some moves
    game.fire_vertex(q)  # Fire vertex B
    assert game.get_current_state()[q] == -5  # -3 - 2 = -5 (degree of q is 2)

    game.borrow_vertex(q)  # Borrow at vertex B
    assert game.get_current_state()[q] == -3  # -5 + 2 = -3


def test_full_output_matches(example_setup, capsys):
    """
    Test that the full output of running the main routine matches the expected output.
    This test partially emulates the main function but captures and checks the output.
    """
    G, D, q = example_setup

    # Create a DollarGame instance
    game = DollarGame(G, D)

    # Print initial state
    print("Initial state:")
    print(game)
    print(f"Total money in system: {game.get_degree()}")
    print(f"Is winnable? {game.is_winnable()}")
    print()

    # Try some moves
    print("After vertex B lends:")
    game.fire_vertex(q)
    print(game)
    print()

    print("After vertex B borrows:")
    game.borrow_vertex(q)
    print(game)
    print()

    # Check if we've won
    print(f"Is current state effective? {game.is_effective()}")
    print(f"Current wealth distribution: {game.get_current_state()}")

    # Capture and verify output
    captured = capsys.readouterr()
    assert "Initial state:" in captured.out
    assert "Total money in system: 2" in captured.out
    assert "Is winnable?" in captured.out
    assert "After vertex B lends:" in captured.out
    assert "After vertex B borrows:" in captured.out
    assert "Is current state effective?" in captured.out
    assert "Current wealth distribution:" in captured.out
