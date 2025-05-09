import pytest
from chipfiring import CFGraph, CFiringScript


@pytest.fixture
def sample_graph():
    """Provides a simple graph for testing."""
    vertices = {"v1", "v2", "v3"}
    edges = [("v1", "v2", 1), ("v2", "v3", 2)]
    return CFGraph(vertices, edges)


def test_cfiringscript_init_valid(sample_graph):
    """Test CFiringScript initialization with a valid script."""
    script_dict = {"v1": 2, "v3": -1}
    firing_script = CFiringScript(sample_graph, script_dict)
    assert firing_script.script == {"v1": 2, "v3": -1, "v2": 0}
    assert firing_script.get_firings("v1") == 2
    assert firing_script.get_firings("v2") == 0  # Not in script
    assert firing_script.get_firings("v3") == -1


def test_cfiringscript_init_invalid_vertex(sample_graph):
    """Test CFiringScript initialization with a vertex not in the graph."""
    script_dict = {"v1": 2, "v4": 1}  # v4 is not in sample_graph
    with pytest.raises(
        ValueError, match="Vertex 'v4' in the script is not present in the graph."
    ):
        CFiringScript(sample_graph, script_dict)


def test_cfiringscript_get_firings(sample_graph):
    """Test the get_firings method."""
    script_dict = {"v1": 5, "v2": -3}
    firing_script = CFiringScript(sample_graph, script_dict)
    assert firing_script.get_firings("v1") == 5
    assert firing_script.get_firings("v2") == -3
    assert firing_script.get_firings("v3") == 0  # Not explicitly in script


def test_cfiringscript_get_firings_invalid_vertex(sample_graph):
    """Test get_firings with a vertex name not in the graph."""
    script_dict = {"v1": 1}
    firing_script = CFiringScript(sample_graph, script_dict)
    with pytest.raises(ValueError, match="Vertex 'v4' is not present in the graph."):
        firing_script.get_firings("v4")


def test_cfiringscript_property(sample_graph):
    """Test the script property."""
    script_dict = {"v2": 10, "v3": -5}
    firing_script = CFiringScript(sample_graph, script_dict)
    # The property should return the original mapping, including only specified vertices
    expected_script = {"v2": 10, "v3": -5, "v1": 0}
    assert firing_script.script == expected_script


def test_cfiringscript_empty_script(sample_graph):
    """Test CFiringScript with an empty script dictionary."""
    firing_script = CFiringScript(sample_graph, {})
    assert firing_script.get_firings("v1") == 0
    assert firing_script.get_firings("v2") == 0
    assert firing_script.get_firings("v3") == 0
    assert firing_script.script == {"v1": 0, "v2": 0, "v3": 0}
