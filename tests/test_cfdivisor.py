import pytest
from chipfiring.CFDivisor import CFDivisor
from chipfiring.CFGraph import CFGraph

@pytest.fixture
def sample_graph():
    """Create a sample graph for testing."""
    vertices = {"A", "B", "C"}
    edges = [("A", "B", 2), ("B", "C", 1), ("A", "C", 1)]
    return CFGraph(vertices, edges)

def test_divisor_creation(sample_graph):
    """Test basic divisor creation."""
    degrees = [("A", 2), ("B", -1), ("C", 0)]
    divisor = CFDivisor(sample_graph, degrees)
    
    # Test degrees were set correctly
    assert divisor.get_degree("A") == 2
    assert divisor.get_degree("B") == -1
    assert divisor.get_degree("C") == 0
    
    # Test total degree calculation
    assert divisor.total_degree == 1  # 2 + (-1) + 0 = 1

def test_divisor_duplicate_vertices(sample_graph):
    """Test that duplicate vertex names in degrees are not allowed."""
    degrees = [("A", 2), ("A", 1), ("B", -1)]
    
    with pytest.raises(ValueError, match="Duplicate vertex names are not allowed"):
        CFDivisor(sample_graph, degrees)

def test_divisor_invalid_vertex(sample_graph):
    """Test that using non-existent vertices raises an error."""
    degrees = [("A", 2), ("D", 1)]  # D is not in the graph
    
    with pytest.raises(ValueError, match="Vertex D not found in graph"):
        CFDivisor(sample_graph, degrees)

def test_get_degree_invalid_vertex(sample_graph):
    """Test getting degree of non-existent vertex."""
    divisor = CFDivisor(sample_graph, [("A", 2), ("B", -1), ("C", 0)])
    
    with pytest.raises(ValueError, match="Vertex D not in divisor"):
        divisor.get_degree("D")

def test_get_total_degree(sample_graph):
    """Test total degree calculation with various configurations."""
    # Test positive total
    divisor1 = CFDivisor(sample_graph, [("A", 2), ("B", 1), ("C", 0)])
    assert divisor1.get_total_degree() == 3
    
    # Test negative total
    divisor2 = CFDivisor(sample_graph, [("A", -2), ("B", -1), ("C", 0)])
    assert divisor2.get_total_degree() == -3
    
    # Test zero total
    divisor3 = CFDivisor(sample_graph, [("A", 1), ("B", -1), ("C", 0)])
    assert divisor3.get_total_degree() == 0

def test_empty_degrees(sample_graph):
    """Test creating a divisor with empty degrees list."""
    divisor = CFDivisor(sample_graph, [])
    
    # All vertices should have degree 0
    assert divisor.get_degree("A") == 0
    assert divisor.get_degree("B") == 0
    assert divisor.get_degree("C") == 0
    assert divisor.get_total_degree() == 0 