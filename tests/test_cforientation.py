import pytest
from chipfiring.CFOrientation import CFOrientation
from chipfiring.CFGraph import CFGraph

@pytest.fixture
def sample_graph():
    """Create a sample graph for testing."""
    vertices = {"A", "B", "C"}
    edges = [("A", "B", 2), ("B", "C", 1), ("A", "C", 1)]
    return CFGraph(vertices, edges)

def test_orientation_creation(sample_graph):
    """Test basic orientation creation."""
    orientations = [("A", "B"), ("B", "C")]
    orientation = CFOrientation(sample_graph, orientations)
    
    # Test orientations were set correctly
    assert orientation.get_orientation("A", "B") == ("A", "B")
    assert orientation.get_orientation("B", "C") == ("B", "C")
    assert orientation.get_orientation("A", "C") is None  # No orientation set

def test_orientation_invalid_edge(sample_graph):
    """Test that using non-existent edges raises an error."""
    orientations = [("A", "B"), ("B", "D")]  # B-D edge doesn't exist
    
    with pytest.raises(ValueError, match="Edge B-D not found in graph"):
        CFOrientation(sample_graph, orientations)

def test_orientation_duplicate_edges(sample_graph):
    """Test that duplicate edge orientations raise an error."""
    orientations = [("A", "B"), ("B", "A")]  # Same edge, opposite directions
    
    with pytest.raises(ValueError, match="Multiple orientations specified for edge"):
        CFOrientation(sample_graph, orientations)

def test_orientation_states(sample_graph):
    """Test orientation states and their relationships."""
    orientations = [("A", "B")]
    orientation = CFOrientation(sample_graph, orientations)
    
    # Test source/sink relationships
    assert orientation.is_source("A", "B") is True
    assert orientation.is_sink("A", "B") is False
    assert orientation.is_source("B", "A") is False
    assert orientation.is_sink("B", "A") is True
    
    # Test unoriented edge
    assert orientation.is_source("A", "C") is None
    assert orientation.is_sink("A", "C") is None

def test_orientation_degrees(sample_graph):
    """Test in-degree and out-degree calculations."""
    # A->B (valence 2), A->C (valence 1)
    orientations = [("A", "B"), ("A", "C")]
    orientation = CFOrientation(sample_graph, orientations)
    
    # Test out-degrees
    assert orientation.get_out_degree("A") == 3  # 2 from A->B, 1 from A->C
    assert orientation.get_out_degree("B") == 0
    assert orientation.get_out_degree("C") == 0
    
    # Test in-degrees
    assert orientation.get_in_degree("A") == 0
    assert orientation.get_in_degree("B") == 2  # From A->B
    assert orientation.get_in_degree("C") == 1  # From A->C

def test_orientation_invalid_vertex(sample_graph):
    """Test operations with invalid vertices."""
    orientation = CFOrientation(sample_graph, [("A", "B")])
    
    # Test get_orientation with invalid vertex
    with pytest.raises(ValueError, match="Edge D-A not found in graph"):
        orientation.get_orientation("D", "A")
    
    # Test is_source with invalid vertex
    with pytest.raises(ValueError, match="Edge D-A not found in graph"):
        orientation.is_source("D", "A")
    
    # Test is_sink with invalid vertex
    with pytest.raises(ValueError, match="Edge D-A not found in graph"):
        orientation.is_sink("D", "A")
    
    # Test get_in_degree with invalid vertex
    with pytest.raises(ValueError, match="Vertex D not found in graph"):
        orientation.get_in_degree("D")
    
    # Test get_out_degree with invalid vertex
    with pytest.raises(ValueError, match="Vertex D not found in graph"):
        orientation.get_out_degree("D")

def test_orientation_edge_valence(sample_graph):
    """Test that edge valence is correctly considered in degree calculations."""
    # Orient the edge with valence 2 (A-B)
    orientation = CFOrientation(sample_graph, [("A", "B")])
    
    assert orientation.get_out_degree("A") == 2  # Valence of A-B is 2
    assert orientation.get_in_degree("B") == 2   # Valence of A-B is 2

def test_empty_orientation(sample_graph):
    """Test orientation with no initial orientations."""
    orientation = CFOrientation(sample_graph, [])
    
    # All edges should have no orientation
    assert orientation.get_orientation("A", "B") is None
    assert orientation.get_orientation("B", "C") is None
    assert orientation.get_orientation("A", "C") is None
    
    # All vertices should have zero in/out degrees
    assert orientation.get_in_degree("A") == 0
    assert orientation.get_out_degree("A") == 0
    assert orientation.get_in_degree("B") == 0
    assert orientation.get_out_degree("B") == 0
    assert orientation.get_in_degree("C") == 0
    assert orientation.get_out_degree("C") == 0 