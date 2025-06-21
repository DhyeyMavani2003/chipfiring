from __future__ import annotations
from dash import Dash, html
import dash_cytoscape as cyto
from .CFGraph import CFGraph, Vertex
from .CFDivisor import CFDivisor
from .CFOrientation import CFOrientation

def _graph_to_cytoscape_elements(graph: CFGraph):
    """Converts a CFGraph object to a list of elements for Dash Cytoscape."""
    nodes = []
    for vertex in graph.vertices:
        nodes.append({
            'data': {
                'id': vertex.name, 
                'label': vertex.name,
                'firing_type': 'neutral',
                'divisor_sign': 'neutral_divisor_sign'
            }
        })

    edges = []
    # Keep track of added edges to avoid duplicates in undirected graph
    added_edges = set()
    for v1 in graph.graph:
        for v2, valence in graph.graph[v1].items():
            # Ensure edge is added only once for undirected graph
            # Sort by name to create a canonical representation of the edge
            edge_pair = tuple(sorted((v1.name, v2.name)))
            if edge_pair not in added_edges:
                for i in range(valence):
                    edges.append({
                        'data': {
                            'source': v1.name,
                            'target': v2.name,
                            'id': f'{edge_pair[0]}-{edge_pair[1]}-{i}',
                            'oriented': False,
                            'arrow_shape': 'none'
                        }
                    })
                added_edges.add(edge_pair)
    
    return nodes + edges

def _divisor_to_cytoscape_elements(divisor: CFDivisor):
    """Converts a CFDivisor object to a list of elements for Dash Cytoscape."""
    elements = _graph_to_cytoscape_elements(divisor.graph)
    for element in elements:
        if 'source' in element.get('data', {}): # It's an edge
            element['data']['arrow_shape'] = 'none'
        elif 'id' in element.get('data', {}) and 'label' in element.get('data', {}) and 'firing_type' in element.get('data', {}): # It's a node
            node_id = element['data']['id']
            vertex_obj = Vertex(node_id)
            if vertex_obj in divisor.degrees:
                chips = divisor.degrees[vertex_obj]
                element['data']['label'] = f"{node_id}\n{chips}"
                if chips < 0:
                    element['data']['divisor_sign'] = 'negative'
                else:
                    element['data']['divisor_sign'] = 'non-negative'
            else:
                element['data']['label'] = f"{node_id}\nN/A"
                element['data']['divisor_sign'] = 'neutral_divisor_sign'
    return elements

def _orientation_to_cytoscape_elements(orientation_obj: CFOrientation):
    """Converts a CFOrientation object to a list of elements for Dash Cytoscape."""
    elements = _graph_to_cytoscape_elements(orientation_obj.graph)

    for element in elements:
        if 'source' in element.get('data', {}): # It's an edge
            edge_id_parts = element['data']['id'].split('-')
            id_v1_name = edge_id_parts[0]
            id_v2_name = edge_id_parts[1]

            oriented_pair = orientation_obj.get_orientation(id_v1_name, id_v2_name)

            if oriented_pair:
                actual_source, actual_target = oriented_pair
                element['data']['source'] = actual_source
                element['data']['target'] = actual_target
                element['data']['oriented'] = True
                element['data']['arrow_shape'] = 'triangle'
            else:
                # Edge has NO_ORIENTATION in CFOrientation object
                element['data']['oriented'] = False
                element['data']['arrow_shape'] = 'none'
                # The source and target remain as arbitrarily assigned by graph_to_cytoscape_elements.
                # The stylesheet will hide the arrow for these.
    return elements

# Base stylesheet for all visualizations
BASE_STYLESHEET = [
    {
        'selector': 'node', # Default node style (also for neutral firing type)
        'style': {
            'label': 'data(label)',
            'background-color': '#D3D3D3', # Default Light Gray for nodes not otherwise specified
            'color': '#000000', # Black text for better contrast on light gray
            'text-outline-width': 1,
            'text-outline-color': '#D3D3D3',
            'text-wrap': 'wrap',          
            'text-valign': 'center',      
            'text-halign': 'center',      
            'width': '50px',
            'height': '50px',
            'font-size': '10px'
        }
    },
    {
        'selector': 'node[divisor_sign = "non-negative"]',
        'style': {
            'background-color': '#28a745', # Green for non-negative divisor
            'text-outline-color': '#28a745',
            'color': '#ffffff' 
        }
    },
    {
        'selector': 'node[divisor_sign = "negative"]',
        'style': {
            'background-color': '#dc3545', # Red for negative divisor
            'text-outline-color': '#dc3545',
            'color': '#ffffff' 
        }
    },
    {
        'selector': 'node[is_q = "true"]',
        'style': {
            'border-width': '3px',
            'border-color': '#007bff' # Blue border for q
        }
    },
    {
        'selector': 'node[is_unburnt = "true"]',
        'style': {
            'background-color': '#ffc107' # Yellow for unburnt
        }
    },
    {
        'selector': 'node[is_burnt = "true"]',
        'style': {
            'background-color': '#6c757d' # Dark gray for burnt
        }
    },
    {
        'selector': 'node[is_in_firing_set = "true"]',
        'style': {
            'border-width': '5px',
            'border-color': '#ffc107',
            'border-style': 'solid'
        }
    },
    {
        'selector': 'edge',
        'style': {
            'line-color': '#9DBFB5',
            'width': 2,
            'curve-style': 'bezier',
            'control-point-step-size': '40px',
            'target-arrow-shape': 'data(arrow_shape)',
            'target-arrow-color': '#555'
        }
    }
]

def visualize(cf_object: any):
    """ Creates and runs a Dash app to visualize a chip-firing object.
    
    Args:
        cf_object: The chip-firing object (CFGraph, CFDivisor, CFOrientation).
        debug: Whether to run the Dash app in debug mode.
        
    Raises:
        TypeError: If the object type is not supported for visualization.
    """
    title = "Chip-Firing Visualization"
    elements = []
    
    if isinstance(cf_object, CFGraph):
        title = "Graph Visualization"
        elements = _graph_to_cytoscape_elements(cf_object)
        for el in elements:
            if 'source' in el.get('data', {}): # it's an edge
                el['data']['arrow_shape'] = 'none'
    elif isinstance(cf_object, CFDivisor):
        title = "Divisor Visualization"
        elements = _divisor_to_cytoscape_elements(cf_object)
    elif isinstance(cf_object, CFOrientation):
        title = "Orientation Visualization"
        elements = _orientation_to_cytoscape_elements(cf_object)
    else:
        raise TypeError(f"Visualization not supported for object of type {type(cf_object).__name__}")
        
    app = Dash(__name__)
    
    app.layout = html.Div([
        html.H1("Chip-Firing Visualizer"),
        html.H2(title),
        cyto.Cytoscape(
            id='cytoscape-graph',
            elements=elements, 
            style={'width': '100%', 'height': '600px'},
            layout={
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
            },
            stylesheet=BASE_STYLESHEET
        )
    ])

    app.run(debug=False)