import pytest
from unittest.mock import patch, MagicMock

from chipfiring import CFGraph, Vertex, CFDivisor, CFOrientation
from chipfiring.CFVisualizer import (
    _graph_to_cytoscape_elements,
    _divisor_to_cytoscape_elements,
    _orientation_to_cytoscape_elements,
    visualize,
    BASE_STYLESHEET
)
from chipfiring.CFOrientation import OrientationState

# Sample data
V1, V2, V3 = Vertex("V1"), Vertex("V2"), Vertex("V3")

@pytest.fixture
def empty_graph():
    return CFGraph(set(), [])

@pytest.fixture
def simple_graph():
    vertices = {V1.name, V2.name}
    edges = [(V1.name, V2.name, 1)]
    return CFGraph(vertices, edges)

@pytest.fixture
def graph_with_three_vertices_two_edges():
    vertices = {V1.name, V2.name, V3.name}
    edges = [(V1.name, V2.name, 1), (V2.name, V3.name, 1)]
    return CFGraph(vertices, edges)

@pytest.fixture
def graph_with_parallel_edges():
    vertices = {V1.name, V2.name, V3.name}
    edges = [(V1.name, V2.name, 2), (V2.name, V3.name, 1)]
    return CFGraph(vertices, edges)

# Tests for _graph_to_cytoscape_elements

def test_graph_to_cytoscape_empty_graph(empty_graph):
    elements = _graph_to_cytoscape_elements(empty_graph)
    assert len(elements) == 0

def test_graph_to_cytoscape_single_node_no_edges():
    g = CFGraph({V1.name}, [])
    elements = _graph_to_cytoscape_elements(g)
    assert len(elements) == 1
    node = elements[0]
    assert node['data']['id'] == V1.name
    assert node['data']['label'] == V1.name
    assert node['data']['divisor_sign'] == 'neutral_divisor_sign'

def test_graph_to_cytoscape_simple_graph(simple_graph):
    elements = _graph_to_cytoscape_elements(simple_graph)
    
    nodes = [el for el in elements if 'source' not in el['data']]
    edges = [el for el in elements if 'source' in el['data']]

    assert len(nodes) == 2
    assert len(edges) == 1

    # Check nodes
    node_names = {node['data']['id'] for node in nodes}
    assert node_names == {V1.name, V2.name}
    for node in nodes:
        assert node['data']['label'] == node['data']['id']
        assert node['data']['divisor_sign'] == 'neutral_divisor_sign'

    # Check edge
    edge = edges[0]
    # Edge ID is sorted by vertex names
    expected_edge_id = f"{min(V1.name, V2.name)}-{max(V1.name, V2.name)}-0"
    assert edge['data']['id'] == expected_edge_id
    assert ( (edge['data']['source'] == V1.name and edge['data']['target'] == V2.name) or \
             (edge['data']['source'] == V2.name and edge['data']['target'] == V1.name) )
    assert not edge['data']['oriented']
    assert edge['data']['arrow_shape'] == 'none'

def test_graph_to_cytoscape_parallel_edges(graph_with_parallel_edges):
    elements = _graph_to_cytoscape_elements(graph_with_parallel_edges)
    nodes = [el for el in elements if 'source' not in el['data']]
    edges = [el for el in elements if 'source' in el['data']]

    assert len(nodes) == 3
    assert len(edges) == 3 # V1-V2 (twice), V2-V3 (once)

    v1_v2_edges = [e for e in edges if V1.name in e['data']['id'] and V2.name in e['data']['id']]
    v2_v3_edges = [e for e in edges if V2.name in e['data']['id'] and V3.name in e['data']['id']]
    
    assert len(v1_v2_edges) == 2
    assert len(v2_v3_edges) == 1

    expected_v1_v2_id_0 = f"{min(V1.name, V2.name)}-{max(V1.name, V2.name)}-0"
    expected_v1_v2_id_1 = f"{min(V1.name, V2.name)}-{max(V1.name, V2.name)}-1"
    edge_ids = {e['data']['id'] for e in v1_v2_edges}
    assert {expected_v1_v2_id_0, expected_v1_v2_id_1} == edge_ids

    for edge in edges:
        assert not edge['data']['oriented']
        assert edge['data']['arrow_shape'] == 'none'

# Tests for _divisor_to_cytoscape_elements

@pytest.fixture
def simple_divisor(simple_graph):
    degrees_data = [(V1.name, 5), (V2.name, -2)]
    return CFDivisor(simple_graph, degrees_data)

@pytest.fixture
def divisor_with_unspecified_node(graph_with_three_vertices_two_edges):
    # V3 will have no specified degree (defaults to 0)
    degrees_data = [(V1.name, 3), (V2.name, 0)]
    return CFDivisor(graph_with_three_vertices_two_edges, degrees_data)

def test_divisor_to_cytoscape_elements(simple_divisor):
    elements = _divisor_to_cytoscape_elements(simple_divisor)
    nodes = {el['data']['id']: el['data'] for el in elements if 'source' not in el['data']}
    edges = [el for el in elements if 'source' in el['data']]

    assert len(nodes) == 2
    assert len(edges) == 1

    # Check V1
    assert nodes[V1.name]['label'] == f"{V1.name}\n5"
    assert nodes[V1.name]['divisor_sign'] == 'non-negative'
    
    # Check V2
    assert nodes[V2.name]['label'] == f"{V2.name}\n-2"
    assert nodes[V2.name]['divisor_sign'] == 'negative'

    # Check edge
    for edge in edges:
        assert edge['data']['arrow_shape'] == 'none'
        assert not edge['data']['oriented'] # Should remain false from graph_to_cytoscape

def test_divisor_to_cytoscape_unspecified_and_zero_degree(divisor_with_unspecified_node):
    elements = _divisor_to_cytoscape_elements(divisor_with_unspecified_node)
    nodes = {el['data']['id']: el['data'] for el in elements if 'source' not in el['data']}
    edges = [el for el in elements if 'source' in el['data']]

    assert len(nodes) == 3
    assert len(edges) == 2

    # Check V1 (positive)
    assert nodes[V1.name]['label'] == f"{V1.name}\n3"
    assert nodes[V1.name]['divisor_sign'] == 'non-negative'

    # Check V2 (zero)
    assert nodes[V2.name]['label'] == f"{V2.name}\n0"
    assert nodes[V2.name]['divisor_sign'] == 'non-negative'

    # Check V3 (N/A) -> Now defaults to 0
    assert nodes[V3.name]['label'] == f"{V3.name}\n0"
    assert nodes[V3.name]['divisor_sign'] == 'non-negative' # 0 is non-negative

    for edge in edges:
        assert edge['data']['arrow_shape'] == 'none' 

# Tests for _orientation_to_cytoscape_elements

@pytest.fixture
def simple_orientation(simple_graph):
    o = CFOrientation(simple_graph, [])
    # Orient V1 -> V2
    o.set_orientation(V1, V2, OrientationState.SOURCE_TO_SINK)
    return o

@pytest.fixture
def orientation_with_mixed_and_no_orientation(graph_with_three_vertices_two_edges):
    o = CFOrientation(graph_with_three_vertices_two_edges, [])
    # V1 -> V2
    o.set_orientation(V1, V2, OrientationState.SOURCE_TO_SINK)
    # V3 -> V2 (reverse of graph edge V2-V3)
    o.set_orientation(V3, V2, OrientationState.SOURCE_TO_SINK) 
    # Edge V2-V3 in graph becomes V3->V2. The third edge (if any, e.g. parallel) would be NO_ORIENTATION.
    # In this graph_with_three_vertices_two_edges, we only have V1-V2 and V2-V3.
    # So, get_orientation(V2,V3) will return (V3,V2)
    # If there was another edge between V2,V3 in the graph, it would be NO_ORIENTATION by default.
    return o

@pytest.fixture
def orientation_with_parallel_edges(graph_with_parallel_edges):
    o = CFOrientation(graph_with_parallel_edges, [])
    # Orient one V1-V2 edge as V1 -> V2
    o.set_orientation(V1, V2, OrientationState.SOURCE_TO_SINK) 
    # The other V1-V2 edge will remain NO_ORIENTATION as set_orientation only handles one edge implicitly
    # For CFOrientation, it orients one of the parallel edges if multiple exist. 
    # The current implementation of _orientation_to_cytoscape_elements will apply this one orientation
    # to ALL cytoscape edges between V1 and V2 because it calls get_orientation(v1_name, v2_name)
    # which returns a single orientation status for the pair, not for each parallel edge instance.
    # This is a nuance of how CFOrientation handles multi-edges vs how cytoscape elements are generated.
    # The test will reflect the current behavior of _orientation_to_cytoscape_elements.

    # Orient V2 -> V3
    o.set_orientation(V2, V3, OrientationState.SOURCE_TO_SINK)
    return o

def test_orientation_to_cytoscape_elements_simple(simple_orientation):
    elements = _orientation_to_cytoscape_elements(simple_orientation)
    nodes = [el for el in elements if 'source' not in el['data']]
    edges = [el for el in elements if 'source' in el['data']]

    assert len(nodes) == 2
    assert len(edges) == 1
    edge = edges[0]

    assert edge['data']['source'] == V1.name
    assert edge['data']['target'] == V2.name
    assert edge['data']['oriented']
    assert edge['data']['arrow_shape'] == 'triangle'

def test_orientation_to_cytoscape_mixed_orientations(orientation_with_mixed_and_no_orientation):
    elements = _orientation_to_cytoscape_elements(orientation_with_mixed_and_no_orientation)
    edges = [el for el in elements if 'source' in el['data']]
    assert len(edges) == 2

    edge_v1_v2 = next(e for e in edges if V1.name in e['data']['id'] and V2.name in e['data']['id'])
    edge_v2_v3 = next(e for e in edges if V2.name in e['data']['id'] and V3.name in e['data']['id'])
    
    # V1 -> V2
    assert edge_v1_v2['data']['source'] == V1.name
    assert edge_v1_v2['data']['target'] == V2.name
    assert edge_v1_v2['data']['oriented']
    assert edge_v1_v2['data']['arrow_shape'] == 'triangle'

    # V2-V3 edge in graph was oriented as V3 -> V2
    assert edge_v2_v3['data']['source'] == V3.name 
    assert edge_v2_v3['data']['target'] == V2.name
    assert edge_v2_v3['data']['oriented']
    assert edge_v2_v3['data']['arrow_shape'] == 'triangle'

def test_orientation_to_cytoscape_no_orientation_defaults():
    # Graph with an edge, but no orientation set in CFOrientation object
    g = CFGraph({V1.name, V2.name}, [(V1.name, V2.name, 1)])
    o = CFOrientation(g, []) # Pass empty list for orientations
    
    elements = _orientation_to_cytoscape_elements(o)
    edge = [el for el in elements if 'source' in el['data']][0]

    # Source/target can be either way, as long as they are consistent with graph
    assert ( (edge['data']['source'] == V1.name and edge['data']['target'] == V2.name) or \
             (edge['data']['source'] == V2.name and edge['data']['target'] == V1.name) )
    assert not edge['data']['oriented']
    assert edge['data']['arrow_shape'] == 'none'

def test_orientation_to_cytoscape_parallel_edges_behavior(orientation_with_parallel_edges):
    elements = _orientation_to_cytoscape_elements(orientation_with_parallel_edges)
    edges = [el for el in elements if 'source' in el['data']]
    v1_v2_edges = [e for e in edges if V1.name in e['data']['id'] and V2.name in e['data']['id']]
    v2_v3_edge = next(e for e in edges if V2.name in e['data']['id'] and V3.name in e['data']['id'])

    assert len(v1_v2_edges) == 2
    
    # All V1-V2 edges will be V1->V2 due to CFOrientation behavior with multi-edges
    for edge in v1_v2_edges:
        assert edge['data']['source'] == V1.name
        assert edge['data']['target'] == V2.name
        assert edge['data']['oriented']
        assert edge['data']['arrow_shape'] == 'triangle'

    # V2-V3 edge will be V2->V3
    assert v2_v3_edge['data']['source'] == V2.name
    assert v2_v3_edge['data']['target'] == V3.name
    assert v2_v3_edge['data']['oriented']
    assert v2_v3_edge['data']['arrow_shape'] == 'triangle'

# Tests for visualize function

@patch('chipfiring.CFVisualizer.Dash')
@patch('chipfiring.CFVisualizer.cyto.Cytoscape')
@patch('chipfiring.CFVisualizer._graph_to_cytoscape_elements')
def test_visualize_cfgraph(
    mock_graph_to_elements, mock_cytoscape, mock_dash, simple_graph
):
    mock_app_instance = MagicMock()
    mock_dash.return_value = mock_app_instance
    
    # Initial setup for the first call (optional, could be removed if not strictly needed for a check)
    mock_graph_to_elements.return_value = [{'data': {'id': 'test_node_only'}}]
    # visualize(simple_graph) # First call - potentially remove if not testing a specific state before the main test
    # mock_graph_to_elements.assert_called_once_with(simple_graph) # Corresponding assertion for the first call
    # mock_dash.assert_called_once_with("chipfiring.CFVisualizer") # This would fail if visualize is called again without reset
    # mock_app_instance.run.assert_called_once() # Reset this as well

    # Reset mocks before the main test call or second call
    mock_graph_to_elements.reset_mock()
    mock_dash.reset_mock() # Reset mock_dash
    mock_cytoscape.reset_mock() # Reset mock_cytoscape
    mock_app_instance.reset_mock() # Reset mock_app_instance which is mock_dash.return_value
    mock_dash.return_value = mock_app_instance # Re-assign after reset, if it was recreated

    # Setup for the primary test call that checks the CFGraph specific loop
    mock_graph_to_elements.return_value = [
        {'data': {'id': V1.name, 'label': V1.name}},
        {'data': {'id': V2.name, 'label': V2.name}},
        {'data': {'source': V1.name, 'target': V2.name, 'id': 'V1-V2-0', 'arrow_shape': 'none'}}
    ]
    
    visualize(simple_graph) # This is the call we are primarily interested in for this assertion
    
    mock_graph_to_elements.assert_called_once_with(simple_graph)
    final_elements_arg = mock_cytoscape.call_args[1]['elements']
    for el in final_elements_arg:
        if 'source' in el.get('data',{}):
            assert el['data']['arrow_shape'] == 'none'


    mock_dash.assert_called_once_with("chipfiring.CFVisualizer")
    mock_cytoscape.assert_called_once()
    args, kwargs = mock_cytoscape.call_args
    assert kwargs['id'] == 'cytoscape-graph'
    assert kwargs['elements'] == mock_graph_to_elements.return_value
    assert kwargs['stylesheet'] == BASE_STYLESHEET
    assert 'layout' in kwargs
    assert mock_app_instance.layout is not None
    # Check title in layout
    assert any(child.children == "Graph Visualization" for child in mock_app_instance.layout.children if hasattr(child, 'children') and isinstance(child.children, str))
    mock_app_instance.run.assert_called_once_with(debug=False)

@patch('chipfiring.CFVisualizer.Dash')
@patch('chipfiring.CFVisualizer.cyto.Cytoscape')
@patch('chipfiring.CFVisualizer._divisor_to_cytoscape_elements')
def test_visualize_cfdivisor(
    mock_divisor_to_elements, mock_cytoscape, mock_dash, simple_divisor
):
    mock_app_instance = MagicMock()
    mock_dash.return_value = mock_app_instance
    mock_divisor_to_elements.return_value = [{'data': {'id': 'test_div'}}]

    visualize(simple_divisor)

    mock_divisor_to_elements.assert_called_once_with(simple_divisor)
    mock_dash.assert_called_once_with("chipfiring.CFVisualizer")
    mock_cytoscape.assert_called_once_with(
        id='cytoscape-graph',
        elements=mock_divisor_to_elements.return_value,
        style={'width': '100%', 'height': '600px'},
        layout=ANY_LAYOUT, # we can be more specific if needed, or use a helper
        stylesheet=BASE_STYLESHEET
    )
    assert any(child.children == "Divisor Visualization" for child in mock_app_instance.layout.children if hasattr(child, 'children') and isinstance(child.children, str))
    mock_app_instance.run.assert_called_once_with(debug=False)

@patch('chipfiring.CFVisualizer.Dash')
@patch('chipfiring.CFVisualizer.cyto.Cytoscape')
@patch('chipfiring.CFVisualizer._orientation_to_cytoscape_elements')
def test_visualize_cforientation(
    mock_orientation_to_elements, mock_cytoscape, mock_dash, simple_orientation
):
    mock_app_instance = MagicMock()
    mock_dash.return_value = mock_app_instance
    mock_orientation_to_elements.return_value = [{'data': {'id': 'test_orient'}}]

    visualize(simple_orientation)

    mock_orientation_to_elements.assert_called_once_with(simple_orientation)
    mock_dash.assert_called_once_with("chipfiring.CFVisualizer")
    assert any(child.children == "Orientation Visualization" for child in mock_app_instance.layout.children if hasattr(child, 'children') and isinstance(child.children, str))
    mock_app_instance.run.assert_called_once_with(debug=False)

def test_visualize_unsupported_type():
    class UnsupportedObject:
        pass
    with pytest.raises(TypeError, match="Visualization not supported for object of type UnsupportedObject"):
        visualize(UnsupportedObject())

# Helper for layout matching if needed, or just check existence as done above
ANY_LAYOUT = {
    'name': 'cose',
    'idealEdgeLength': 150,
    'nodeOverlap': 20,
    'refresh': 20,
    'fit': True,
    'padding': 30,
    'randomize': False,
    'componentSpacing': 100,
    'nodeRepulsion': 400000,
    'edgeElasticity': 100,
    'nestingFactor': 5,
    'gravity': 80,
    'numIter': 1000,
    'initialTemp': 200,
    'coolingFactor': 0.95,
    'minTemp': 1.0
} 