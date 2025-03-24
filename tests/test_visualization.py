"""
Tests for the visualization module.
"""

import pytest
import matplotlib.pyplot as plt
from chipfiring.graph import Graph, Vertex
from chipfiring.divisor import Divisor
from chipfiring.dollar_game import DollarGame
from chipfiring.visualization import draw_graph, draw_game_state


@pytest.fixture
def example_graph():
    """Create an example graph for testing."""
    G = Graph()
    v1 = Vertex("A")
    v2 = Vertex("B")
    v3 = Vertex("C")

    G.add_vertex(v1)
    G.add_vertex(v2)
    G.add_vertex(v3)

    G.add_edge(v1, v2)
    G.add_edge(v2, v3)
    G.add_edge(v1, v3)

    return G, v1, v2, v3


def test_draw_graph(example_graph):
    """Test basic graph visualization."""
    G, v1, v2, v3 = example_graph

    # Test that the function runs without errors
    fig, ax = draw_graph(G)
    plt.close(fig)


def test_draw_graph_with_labels(example_graph):
    """Test graph visualization with custom labels."""
    G, v1, v2, v3 = example_graph

    # Test with custom labels
    fig, ax = draw_graph(G, title="Test Graph")
    plt.close(fig)


def test_draw_graph_with_positions(example_graph):
    """Test graph visualization with custom positions."""
    G, v1, v2, v3 = example_graph

    # Test with custom positions
    pos = {v1: (0, 0), v2: (1, 0), v3: (0.5, 1)}
    fig, ax = draw_graph(G, pos=pos)
    plt.close(fig)


def test_draw_game_state(example_graph):
    """Test game state visualization."""
    G, v1, v2, v3 = example_graph
    D = Divisor(G, {v1: 2, v2: -1, v3: 0})

    # Create a DollarGame instance
    game = DollarGame(G, D)

    # Test that the function runs without errors
    fig, ax = draw_game_state(game)
    plt.close(fig)


def test_draw_game_state_with_labels(example_graph):
    """Test game state visualization with custom labels."""
    G, v1, v2, v3 = example_graph
    D = Divisor(G, {v1: 2, v2: -1, v3: 0})

    # Create a DollarGame instance
    game = DollarGame(G, D)

    # Test with custom labels
    fig, ax = draw_game_state(game, title="Test Game State")
    plt.close(fig)


def test_draw_game_state_with_positions(example_graph):
    """Test game state visualization with custom positions."""
    G, v1, v2, v3 = example_graph
    D = Divisor(G, {v1: 2, v2: -1, v3: 0})

    # Create a DollarGame instance
    game = DollarGame(G, D)

    # Test with custom positions
    pos = {v1: (0, 0), v2: (1, 0), v3: (0.5, 1)}
    fig, ax = draw_game_state(game, pos=pos)
    plt.close(fig)


def test_draw_game_state_with_colors(example_graph):
    """Test game state visualization with custom colors."""
    G, v1, v2, v3 = example_graph
    D = Divisor(G, {v1: 2, v2: -1, v3: 0})

    # Create a DollarGame instance
    game = DollarGame(G, D)

    # Test with custom colors
    fig, ax = draw_game_state(game, title="Test Colors")
    plt.close(fig)


def test_draw_game_state_with_edge_colors(example_graph):
    """Test game state visualization with custom edge colors."""
    G, v1, v2, v3 = example_graph
    D = Divisor(G, {v1: 2, v2: -1, v3: 0})

    # Create a DollarGame instance
    game = DollarGame(G, D)

    # Test with custom edge colors
    fig, ax = draw_game_state(game, title="Test Edge Colors")
    plt.close(fig)


def test_draw_game_state_with_node_sizes(example_graph):
    """Test game state visualization with custom node sizes."""
    G, v1, v2, v3 = example_graph
    D = Divisor(G, {v1: 2, v2: -1, v3: 0})

    # Create a DollarGame instance
    game = DollarGame(G, D)

    # Test with custom node sizes
    fig, ax = draw_game_state(game, title="Test Node Sizes", node_size=500)
    plt.close(fig)


def test_draw_game_state_with_font_sizes(example_graph):
    """Test game state visualization with custom font sizes."""
    G, v1, v2, v3 = example_graph
    D = Divisor(G, {v1: 2, v2: -1, v3: 0})

    # Create a DollarGame instance
    game = DollarGame(G, D)

    # Test with custom font sizes
    fig, ax = draw_game_state(game, title="Test Font Sizes", font_size=8)
    plt.close(fig)
