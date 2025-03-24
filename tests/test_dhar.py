"""
Tests for Dhar's algorithm implementation.
"""

import pytest
from chipfiring.graph import Graph, Vertex
from chipfiring.divisor import Divisor
from chipfiring.dollar_game import DollarGame
from chipfiring.dhar import (
    outdegree_to_set,
    find_legal_firing_set,
    is_q_reduced,
    send_debt_to_q,
    q_reduce,
    is_winnable_dhar,
    get_winning_strategy_dhar,
)


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


def test_outdegree_to_set(example_graph):
    """Test the outdegree calculation with respect to a subset."""
    G, v1, v2, v3 = example_graph

    # Outdegree of v1 with respect to {v1, v2}
    assert outdegree_to_set(G, v1, {v1, v2}) == 1  # Edge to v3

    # Outdegree of v1 with respect to {v1}
    assert outdegree_to_set(G, v1, {v1}) == 2  # Edges to v2 and v3

    # Outdegree of v2 with respect to {v1, v2, v3}
    assert outdegree_to_set(G, v2, {v1, v2, v3}) == 0  # No edges outside the set


def test_find_legal_firing_set(example_graph):
    """Test Dhar's algorithm to find legal firing sets."""
    G, v1, v2, v3 = example_graph

    # Create a divisor where all vertices have one chip
    D1 = Divisor(G, {v1: 1, v2: 1, v3: 1})

    # With v1 as the distinguished vertex
    # In our implementation, v2 and v3 will be part of the legal firing set
    # because they need an edge's worth of debt to go negative
    legal_set = find_legal_firing_set(G, D1, v1)
    assert legal_set == {v2, v3}

    # Create a divisor with more chips
    D2 = Divisor(G, {v1: 2, v2: 3, v3: 3})

    # With v1 as the distinguished vertex, both v2 and v3 should be in the legal firing set
    legal_set = find_legal_firing_set(G, D2, v1)
    assert legal_set == {v2, v3}

    # Create a divisor where v2 would catch fire but v3 might not
    # This depends on the specific burning propagation in the algorithm
    D3 = Divisor(G, {v1: 0, v2: 0, v3: 2})

    # Find legal firing set
    legal_set = find_legal_firing_set(G, D3, v1)
    assert v3 in legal_set  # v3 has enough chips to not burn
    assert v2 not in legal_set  # v2 should burn because it has 0 chips

    # Create a divisor where all vertices would burn
    D4 = Divisor(G, {v1: 0, v2: 0, v3: 0})

    # With v1 as the distinguished vertex, the legal firing set should be empty
    # as both v2 and v3 will burn in the algorithm
    legal_set = find_legal_firing_set(G, D4, v1)
    assert legal_set == set()


def test_is_q_reduced(example_graph):
    """Test checking if a divisor is q-reduced."""
    G, v1, v2, v3 = example_graph

    # Create a q-reduced divisor with respect to v1
    # Each non-q vertex has 0 chips, so they would burn in Dhar's algorithm
    D1 = Divisor(G, {v1: 0, v2: 0, v3: 0})
    assert is_q_reduced(G, D1, v1)

    # Create a non-q-reduced divisor with respect to v1
    # v2 and v3 have enough chips to not burn
    D2 = Divisor(G, {v1: 0, v2: 2, v3: 2})
    assert not is_q_reduced(G, D2, v1)

    # Non-q-reduced because v2 has a negative value
    D3 = Divisor(G, {v1: 0, v2: -1, v3: 1})
    assert not is_q_reduced(G, D3, v1)


def test_send_debt_to_q(example_graph):
    """Test debt consolidation at the source vertex."""
    G, v1, v2, v3 = example_graph

    # Create a divisor with negative values at multiple vertices
    D = Divisor(G, {v1: 1, v2: -1, v3: -1})

    # Send debt to v1
    result = send_debt_to_q(G, D, v1)

    # Check that v2 and v3 have non-negative values
    assert result[v2] >= 0
    assert result[v3] >= 0

    # Total degree must be preserved
    assert result.degree() == D.degree()


def test_q_reduce(example_graph):
    """Test q-reduction of a divisor."""
    G, v1, v2, v3 = example_graph

    # Create a divisor
    D = Divisor(G, {v1: 1, v2: 1, v3: 1})

    # Compute the q-reduced divisor with respect to v1
    q_reduced_D = q_reduce(G, D, v1)

    # Check that it's q-reduced
    assert is_q_reduced(G, q_reduced_D, v1)

    # Total degree must be preserved
    assert q_reduced_D.degree() == D.degree()


def test_is_winnable_dhar():
    """Test winnability determination using Dhar's algorithm."""
    # Create a simple graph
    G = Graph()
    v1 = Vertex("A")
    v2 = Vertex("B")

    G.add_vertex(v1)
    G.add_vertex(v2)
    G.add_edge(v1, v2)

    # Create a winnable divisor (total degree = 0)
    D1 = Divisor(G, {v1: 1, v2: -1})
    assert is_winnable_dhar(G, D1)

    # Create an unwinnable divisor (total degree = -1)
    D2 = Divisor(G, {v1: 0, v2: -1})
    assert not is_winnable_dhar(G, D2)


def test_get_winning_strategy_dhar():
    """Test finding a winning strategy using Dhar's algorithm."""
    # Create a simple graph
    G = Graph()
    v1 = Vertex("A")
    v2 = Vertex("B")

    G.add_vertex(v1)
    G.add_vertex(v2)
    G.add_edge(v1, v2)

    # Create a winnable divisor
    D = Divisor(G, {v1: 1, v2: -1})

    # Get a winning strategy
    strategy = get_winning_strategy_dhar(G, D)

    # Strategy should be to borrow at v2
    assert strategy is not None

    # Apply the strategy to a game and check if it becomes effective
    game = DollarGame(G, Divisor(G, {v1: 1, v2: -1}))

    # Apply each move in the strategy
    for v, count in strategy.items():
        if count < 0:  # Borrowing
            for _ in range(-count):
                game.borrow_vertex(v)

    # Check if the final state is effective
    assert game.is_effective()


def test_integration_with_dollar_game(example_graph):
    """Test integration with the DollarGame class."""
    G, v1, v2, v3 = example_graph

    # Create a divisor
    D = Divisor(G, {v1: 0, v2: -1, v3: 2})

    # Create a game
    game = DollarGame(G, D)

    # Check winnability
    assert game.is_winnable()

    # First make sure v2 is non-negative to find a legal firing set
    game.borrow_vertex(v2)

    # Find legal firing set with respect to v1
    legal_set = game.find_legal_firing_set(v1)
    assert legal_set != set()  # Should have a non-empty legal firing set

    # Compute q-reduced divisor
    q_reduced = game.compute_q_reduced_divisor(v1)
    assert is_q_reduced(G, q_reduced, v1)

    # Reset the game and get a winning strategy
    game = DollarGame(G, D)
    strategy = game.get_winning_strategy()
    assert strategy is not None
