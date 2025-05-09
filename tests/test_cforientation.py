import pytest
from chipfiring.CFOrientation import CFOrientation
from chipfiring.CFGraph import CFGraph
from chipfiring import CFDivisor


@pytest.fixture
def sample_graph():
    """Create a sample graph for testing."""
    vertices = {"A", "B", "C"}
    edges = [("A", "B", 2), ("B", "C", 1), ("A", "C", 1)]
    return CFGraph(vertices, edges)


@pytest.fixture
def simple_graph_k3():
    """Provides a simple K3 graph for testing."""
    vertices = {"v1", "v2", "v3"}
    edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
    return CFGraph(vertices, edges)


@pytest.fixture
def graph_with_multi_edges():
    """Provides a graph with multiple edges."""
    vertices = {"a", "b", "c"}
    # a==(2)==b, b==(3)==c
    edges = [("a", "b", 2), ("b", "c", 3)]
    return CFGraph(vertices, edges)


@pytest.fixture
def fully_oriented_k3(simple_graph_k3):
    """Provides a fully oriented K3 graph (v1->v2, v2->v3, v1->v3)."""
    orientations = [("v1", "v2"), ("v2", "v3"), ("v1", "v3")]
    return CFOrientation(simple_graph_k3, orientations)


@pytest.fixture
def partially_oriented_k3(simple_graph_k3):
    """Provides a partially oriented K3 graph (v1->v2 only)."""
    orientations = [("v1", "v2")]
    return CFOrientation(simple_graph_k3, orientations)


@pytest.fixture
def fully_oriented_multi(graph_with_multi_edges):
    """Provides a fully oriented graph with multi-edges (a->b, c->b)."""
    orientations = [("a", "b"), ("c", "b")]
    return CFOrientation(graph_with_multi_edges, orientations)


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
    assert orientation.get_in_degree("B") == 2  # Valence of A-B is 2


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


def test_cforientation_init_valid(simple_graph_k3):
    """Test CFOrientation initialization with valid orientations."""
    orientations = [("v1", "v2"), ("v3", "v2")]
    orientation = CFOrientation(simple_graph_k3, orientations)
    assert orientation.get_orientation("v1", "v2") == ("v1", "v2")
    assert orientation.get_orientation("v2", "v3") == ("v3", "v2")
    assert orientation.get_orientation("v1", "v3") is None  # Unoriented
    assert not orientation.is_full


def test_cforientation_init_full(fully_oriented_k3):
    """Test that a fully specified orientation is marked as full."""
    assert fully_oriented_k3.is_full


def test_cforientation_init_invalid_edge(simple_graph_k3):
    """Test init with an orientation for a non-existent edge."""
    orientations = [("v1", "v4")]  # v4 is not a vertex
    with pytest.raises(ValueError, match="Edge v1-v4 not found in graph"):
        CFOrientation(simple_graph_k3, orientations)

    orientations = [("v1", "v1")]  # Edge v1-v1 doesn't exist (no self-loops)
    with pytest.raises(ValueError, match="Edge v1-v1 not found in graph"):
        CFOrientation(simple_graph_k3, orientations)


def test_cforientation_init_duplicate_orientation(simple_graph_k3):
    """Test init with multiple orientations for the same edge."""
    orientations = [("v1", "v2"), ("v2", "v1")]
    with pytest.raises(
        ValueError, match="Multiple orientations specified for edge v1-v2"
    ):
        CFOrientation(simple_graph_k3, orientations)
    orientations = [("v1", "v2"), ("v1", "v2")]  # Implicit duplicate
    with pytest.raises(
        ValueError, match="Multiple orientations specified for edge v1-v2"
    ):
        CFOrientation(simple_graph_k3, orientations)


def test_get_orientation(fully_oriented_k3, partially_oriented_k3):
    """Test the get_orientation method."""
    # Fully oriented
    assert fully_oriented_k3.get_orientation("v1", "v2") == ("v1", "v2")
    assert fully_oriented_k3.get_orientation("v2", "v1") == (
        "v1",
        "v2",
    )  # Order doesn't matter
    assert fully_oriented_k3.get_orientation("v2", "v3") == ("v2", "v3")
    assert fully_oriented_k3.get_orientation("v1", "v3") == ("v1", "v3")

    # Partially oriented
    assert partially_oriented_k3.get_orientation("v1", "v2") == ("v1", "v2")
    assert partially_oriented_k3.get_orientation("v2", "v3") is None
    assert partially_oriented_k3.get_orientation("v1", "v3") is None


def test_get_orientation_invalid_edge(fully_oriented_k3):
    """Test get_orientation for non-existent edges."""
    with pytest.raises(ValueError, match="Edge v1-v4 not found in graph"):
        fully_oriented_k3.get_orientation("v1", "v4")
    with pytest.raises(ValueError, match="Edge v1-v1 not found in graph"):
        fully_oriented_k3.get_orientation("v1", "v1")


def test_is_source_sink(fully_oriented_k3, partially_oriented_k3):
    """Test the is_source and is_sink methods."""
    # Fully oriented (v1->v2, v2->v3, v1->v3)
    assert fully_oriented_k3.is_source("v1", "v2") is True
    assert fully_oriented_k3.is_sink("v1", "v2") is False
    assert fully_oriented_k3.is_source("v2", "v1") is False  # v1 is source
    assert fully_oriented_k3.is_sink("v2", "v1") is True

    assert fully_oriented_k3.is_source("v2", "v3") is True
    assert fully_oriented_k3.is_sink("v3", "v2") is True

    assert fully_oriented_k3.is_source("v1", "v3") is True
    assert fully_oriented_k3.is_sink("v3", "v1") is True

    # Partially oriented (v1->v2 only)
    assert partially_oriented_k3.is_source("v1", "v2") is True
    assert partially_oriented_k3.is_sink("v2", "v1") is True
    assert partially_oriented_k3.is_source("v2", "v3") is None  # Unoriented
    assert partially_oriented_k3.is_sink("v2", "v3") is None
    assert partially_oriented_k3.is_source("v1", "v3") is None
    assert partially_oriented_k3.is_sink("v1", "v3") is None


def test_get_in_out_degree(fully_oriented_k3, fully_oriented_multi):
    """Test get_in_degree and get_out_degree."""
    # K3: v1->v2, v2->v3, v1->v3
    assert fully_oriented_k3.get_in_degree("v1") == 0
    assert fully_oriented_k3.get_out_degree("v1") == 2
    assert fully_oriented_k3.get_in_degree("v2") == 1  # from v1
    assert fully_oriented_k3.get_out_degree("v2") == 1  # to v3
    assert fully_oriented_k3.get_in_degree("v3") == 2  # from v1, v2
    assert fully_oriented_k3.get_out_degree("v3") == 0

    # Multi-graph: a ->(2) b <-(3) c
    assert fully_oriented_multi.get_in_degree("a") == 0
    assert fully_oriented_multi.get_out_degree("a") == 2  # edge a-b has valence 2
    assert fully_oriented_multi.get_in_degree("b") == 2 + 3  # from a (2), from c (3)
    assert fully_oriented_multi.get_out_degree("b") == 0
    assert fully_oriented_multi.get_in_degree("c") == 0
    assert fully_oriented_multi.get_out_degree("c") == 3  # edge c-b has valence 3


def test_get_degree_invalid_vertex(fully_oriented_k3):
    """Test get_in_degree and get_out_degree with invalid vertex."""
    with pytest.raises(ValueError, match="Vertex v4 not found in graph"):
        fully_oriented_k3.get_in_degree("v4")
    with pytest.raises(ValueError, match="Vertex v4 not found in graph"):
        fully_oriented_k3.get_out_degree("v4")


def test_reverse_orientation(fully_oriented_k3, fully_oriented_multi):
    """Test reversing a full orientation."""
    # K3: v1->v2, v2->v3, v1->v3
    reversed_k3 = fully_oriented_k3.reverse()
    assert reversed_k3.is_full
    # Check reversed edges
    assert reversed_k3.get_orientation("v1", "v2") == ("v2", "v1")
    assert reversed_k3.get_orientation("v2", "v3") == ("v3", "v2")
    assert reversed_k3.get_orientation("v1", "v3") == ("v3", "v1")
    # Check degrees
    assert reversed_k3.get_in_degree("v1") == 2  # Original out-degree
    assert reversed_k3.get_out_degree("v1") == 0
    assert reversed_k3.get_in_degree("v2") == 1  # Original out-degree
    assert reversed_k3.get_out_degree("v2") == 1
    assert reversed_k3.get_in_degree("v3") == 0  # Original out-degree
    assert reversed_k3.get_out_degree("v3") == 2

    # Multi-graph: a ->(2) b <-(3) c
    reversed_multi = fully_oriented_multi.reverse()
    assert reversed_multi.is_full
    # Check reversed edges
    assert reversed_multi.get_orientation("a", "b") == ("b", "a")
    assert reversed_multi.get_orientation("b", "c") == ("b", "c")
    # Check degrees
    assert reversed_multi.get_in_degree("a") == 2  # Original out-degree
    assert reversed_multi.get_out_degree("a") == 0
    assert reversed_multi.get_in_degree("b") == 0  # Original out-degree
    assert reversed_multi.get_out_degree("b") == 2 + 3  # Original in-degree
    assert reversed_multi.get_in_degree("c") == 3  # Original out-degree
    assert reversed_multi.get_out_degree("c") == 0


def test_reverse_orientation_not_full(partially_oriented_k3):
    """Test that reversing a non-full orientation raises an error."""
    assert not partially_oriented_k3.is_full
    with pytest.raises(RuntimeError, match="Cannot reverse a not full orientation"):
        partially_oriented_k3.reverse()


def test_divisor_from_orientation(fully_oriented_k3, fully_oriented_multi):
    """Test creating a divisor from a full orientation."""
    # K3: v1->v2, v2->v3, v1->v3
    # In-degrees: v1=0, v2=1, v3=2
    divisor_k3 = fully_oriented_k3.divisor()
    assert isinstance(divisor_k3, CFDivisor)
    assert (
        divisor_k3.get_degree("v1") == fully_oriented_k3.get_in_degree("v1") - 1
    )  # 0 - 1 = -1
    assert (
        divisor_k3.get_degree("v2") == fully_oriented_k3.get_in_degree("v2") - 1
    )  # 1 - 1 = 0
    assert (
        divisor_k3.get_degree("v3") == fully_oriented_k3.get_in_degree("v3") - 1
    )  # 2 - 1 = 1
    # Total degree = -1 + 0 + 1 = 0. Genus = |E|-|V|+1 = 3-3+1 = 1. Expected total degree = 2g-2 = 0.
    assert divisor_k3.get_total_degree() == 0

    # Multi-graph: a ->(2) b <-(3) c
    # In-degrees: a=0, b=5, c=0
    divisor_multi = fully_oriented_multi.divisor()
    assert isinstance(divisor_multi, CFDivisor)
    assert (
        divisor_multi.get_degree("a") == fully_oriented_multi.get_in_degree("a") - 1
    )  # 0 - 1 = -1
    assert (
        divisor_multi.get_degree("b") == fully_oriented_multi.get_in_degree("b") - 1
    )  # 5 - 1 = 4
    assert (
        divisor_multi.get_degree("c") == fully_oriented_multi.get_in_degree("c") - 1
    )  # 0 - 1 = -1
    # Total degree = -1 + 4 - 1 = 2. Genus = |E|-|V|+1 = (2+3)-3+1 = 3. Expected total degree = 2g-2 = 2*3-2 = 4.
    # Hmm, the total degree formula 2g-2 might only apply for specific divisor classes?
    # Let's just check the sum directly.
    assert divisor_multi.get_total_degree() == 2


def test_divisor_from_orientation_not_full(partially_oriented_k3):
    """Test that creating a divisor from a non-full orientation raises an error."""
    assert not partially_oriented_k3.is_full
    with pytest.raises(
        RuntimeError, match="Cannot create divisor: Orientation is not full"
    ):
        partially_oriented_k3.divisor()


def test_canonical_divisor(simple_graph_k3, graph_with_multi_edges):
    """Test creating the canonical divisor."""
    # K3: Valences v1=2, v2=2, v3=2
    orientation_k3 = CFOrientation(simple_graph_k3, [])  # Orientation doesn't matter
    canonical_k3 = orientation_k3.canonical_divisor()
    assert isinstance(canonical_k3, CFDivisor)
    assert (
        canonical_k3.get_degree("v1") == simple_graph_k3.get_valence("v1") - 2
    )  # 2 - 2 = 0
    assert (
        canonical_k3.get_degree("v2") == simple_graph_k3.get_valence("v2") - 2
    )  # 2 - 2 = 0
    assert (
        canonical_k3.get_degree("v3") == simple_graph_k3.get_valence("v3") - 2
    )  # 2 - 2 = 0
    assert canonical_k3.get_total_degree() == 0

    # Multi-graph: Valences a=2, b=5, c=3
    orientation_multi = CFOrientation(
        graph_with_multi_edges, []
    )  # Orientation doesn't matter
    canonical_multi = orientation_multi.canonical_divisor()
    assert isinstance(canonical_multi, CFDivisor)
    assert (
        canonical_multi.get_degree("a") == graph_with_multi_edges.get_valence("a") - 2
    )  # 2 - 2 = 0
    assert (
        canonical_multi.get_degree("b") == graph_with_multi_edges.get_valence("b") - 2
    )  # 5 - 2 = 3
    assert (
        canonical_multi.get_degree("c") == graph_with_multi_edges.get_valence("c") - 2
    )  # 3 - 2 = 1
    assert canonical_multi.get_total_degree() == 0 + 3 + 1  # 4
    # Check against 2g-2: g = |E|-|V|+1 = (2+3)-3+1 = 3. 2g-2 = 2*3-2 = 4. Matches.
