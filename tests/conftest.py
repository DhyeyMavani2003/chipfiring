"""
Test configuration file for pytest.
"""

import pytest
import numpy as np
from chipfiring.CFGraph import CFGraph, Vertex
from chipfiring.CFDivisor import CFDivisor


@pytest.fixture
def example_graph():
    """Create an example graph for testing."""
    G = CFGraph({"A", "B", "C"}, [])
    v1 = Vertex("A")
    v2 = Vertex("B")
    v3 = Vertex("C")

    G.add_edge("A", "B", 1)
    G.add_edge("B", "C", 1)
    G.add_edge("A", "C", 1)

    return G, v1, v2, v3


@pytest.fixture
def example_divisor(example_graph):
    """Create an example divisor for testing."""
    G, v1, v2, v3 = example_graph
    degrees = [("A", 2), ("B", -1), ("C", 0)]
    D = CFDivisor(G, degrees)
    return D


@pytest.fixture
def random_graph():
    """Create a random graph for testing."""
    vertices = {f"v{i}" for i in range(5)}
    G = CFGraph(vertices, [])
    vertex_list = [Vertex(f"v{i}") for i in range(5)]

    # Add random edges
    for i in range(len(vertex_list)):
        for j in range(i + 1, len(vertex_list)):
            if np.random.random() < 0.5:  # 50% chance of edge
                G.add_edge(f"v{i}", f"v{j}", 1)

    return G, vertex_list


@pytest.fixture
def random_divisor(random_graph):
    """Create a random divisor for testing."""
    G, vertices = random_graph
    degrees = [
        (v.name, np.random.randint(-2, 3)) for v in vertices
    ]  # Random values between -2 and 2
    return CFDivisor(G, degrees)
