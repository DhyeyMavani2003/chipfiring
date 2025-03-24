"""
Test configuration file for pytest.
"""

import pytest
import numpy as np
from chipfiring.graph import Graph, Vertex
from chipfiring.divisor import Divisor


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


@pytest.fixture
def example_divisor(example_graph):
    """Create an example divisor for testing."""
    G, v1, v2, v3 = example_graph
    D = Divisor(G)

    D[v1] = 2
    D[v2] = -1
    D[v3] = 0

    return D


@pytest.fixture
def random_graph():
    """Create a random graph for testing."""
    G = Graph()
    vertices = [Vertex(f"v{i}") for i in range(5)]

    for v in vertices:
        G.add_vertex(v)

    # Add random edges
    for i in range(len(vertices)):
        for j in range(i + 1, len(vertices)):
            if np.random.random() < 0.5:  # 50% chance of edge
                G.add_edge(vertices[i], vertices[j])

    return G, vertices


@pytest.fixture
def random_divisor(random_graph):
    """Create a random divisor for testing."""
    G, vertices = random_graph
    D = Divisor(G)

    for v in vertices:
        D[v] = np.random.randint(-2, 3)  # Random values between -2 and 2

    return D
