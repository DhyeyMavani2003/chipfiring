from __future__ import annotations
from dash import Dash, html, dcc, Input, Output, State, no_update, ctx
import dash_cytoscape as cyto
import math
import os
import networkx as nx
from .CFGraph import CFGraph, Vertex
from .CFDivisor import CFDivisor
from .CFOrientation import CFOrientation
from .CFPlatonicSolids import (
    tetrahedron, cube, octahedron, dodecahedron, icosahedron, complete_graph
)
from .CFChainsOfCycles import basicChain

VERTEX_RADIUS = 25  # half of 50px node width/height


def _make_zero_divisor(graph: CFGraph) -> CFDivisor:
    """Return a CFDivisor with 0 chips on every vertex of graph."""
    return CFDivisor(graph, [(v.name, 0) for v in graph.vertices])


def _make_canonical_divisor(graph: CFGraph) -> CFDivisor:
    """Return the canonical divisor K where K(v) = deg(v) - 2 for each vertex."""
    return CFDivisor(graph, [
        (v.name, sum(graph.graph[v].values()) - 2)
        for v in graph.vertices
    ])


def _graph_from_spec(spec: dict, initial_graph: CFGraph) -> CFGraph:
    """Reconstruct a CFGraph from a stored spec dict (as saved in current-graph-spec store)."""
    if not spec or spec.get('type') == 'initial':
        return initial_graph
    t = spec['type']
    if t == 'tetrahedron': return tetrahedron()
    if t == 'cube':        return cube()
    if t == 'octahedron':  return octahedron()
    if t == 'dodecahedron':return dodecahedron()
    if t == 'icosahedron': return icosahedron()
    if t == 'complete':    return complete_graph(spec['n'])
    if t == 'chain':       return basicChain(spec['lengths'])
    raise ValueError(f"Unknown graph spec type: {t}")


def _compute_spring_layout(graph: CFGraph, width: int = 800, height: int = 600, padding: int = 100):
    """Compute node positions using networkx spring layout, scaled to pixel coordinates."""
    nx_graph = nx.Graph()
    for vertex in graph.vertices:
        nx_graph.add_node(vertex.name)
    for v1 in graph.graph:
        for v2 in graph.graph[v1]:
            nx_graph.add_edge(v1.name, v2.name)

    if len(graph.vertices) == 0:
        return {}

    pos = nx.spring_layout(nx_graph, seed=42)

    # spring_layout returns values in roughly [-1, 1]; scale to pixel coords
    scaled = {}
    for node, (x, y) in pos.items():
        px = (x + 1) / 2 * (width - 2 * padding) + padding
        py = (y + 1) / 2 * (height - 2 * padding) + padding
        scaled[node] = (px, py)
    return scaled


def _chip_indicator_elements(vertex_name: str, cx: float, cy: float, chips: int):
    """Return chip indicator node elements arranged clockwise from 12 o'clock around a vertex.

    Chip radius starts at VERTEX_RADIUS/8 and is halved as needed until all chips fit
    without overlapping on the orbit circle just outside the vertex.
    """
    n_chips = abs(chips)
    chip_type = 'positive_chip' if chips > 0 else 'negative_chip'

    # Find smallest chip radius such that all n_chips fit non-overlapping on the orbit.
    # For N chips on a circle of radius R, adjacent chord = 2*R*sin(π/N) >= 2*chip_r
    # → N_max = floor(π / arcsin(chip_r / R))
    chip_r = VERTEX_RADIUS / 5
    while True:
        orbit_r = VERTEX_RADIUS + chip_r
        max_chips = math.floor(math.pi / math.asin(chip_r / orbit_r))
        if max_chips >= n_chips:
            break
        chip_r /= 2
        if chip_r < 0.05:  # safety lower bound
            break

    orbit_r = VERTEX_RADIUS + chip_r
    elements = []
    for i in range(n_chips):
        # Clockwise from 12 o'clock: angle 0 = top, increasing clockwise
        angle = 2 * math.pi * i / n_chips
        chip_x = cx + orbit_r * math.sin(angle)
        chip_y = cy - orbit_r * math.cos(angle)
        elements.append({
            'data': {
                'id': f'chip_{vertex_name}_{i}',
                'chip_type': chip_type,
                'chip_size': chip_r * 2,
                'parent_vertex': vertex_name,
                'dx': chip_x - cx,
                'dy': chip_y - cy,
            },
            'position': {'x': chip_x, 'y': chip_y},
            'selectable': False,
            'grabbable': False,
        })
    return elements


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
    """Converts a CFDivisor object to a list of elements for Dash Cytoscape.

    Uses a spring layout computed in Python so that chip indicator positions
    can be calculated relative to each vertex.
    """
    positions = _compute_spring_layout(divisor.graph)

    elements = []

    # Vertex nodes with preset positions
    for vertex in divisor.graph.vertices:
        node_id = vertex.name
        pos = positions.get(node_id, (400, 300))
        vertex_obj = Vertex(node_id)
        chips = divisor.degrees.get(vertex_obj)

        if chips is None:
            divisor_sign = 'neutral_divisor_sign'
            label = f"{node_id}\nN/A"
        elif chips < 0:
            divisor_sign = 'negative'
            label = f"{node_id}\n{chips}"
        elif chips == 0:
            divisor_sign = 'zero'
            label = f"{node_id}\n0"
        else:
            divisor_sign = 'positive'
            label = f"{node_id}\n{chips}"

        elements.append({
            'data': {
                'id': node_id,
                'label': label,
                'firing_type': 'neutral',
                'divisor_sign': divisor_sign,
                'chips_count': chips if chips is not None else 0,
            },
            'position': {'x': pos[0], 'y': pos[1]},
        })

    # Edges
    added_edges = set()
    for v1 in divisor.graph.graph:
        for v2, valence in divisor.graph.graph[v1].items():
            edge_pair = tuple(sorted((v1.name, v2.name)))
            if edge_pair not in added_edges:
                for i in range(valence):
                    elements.append({
                        'data': {
                            'source': v1.name,
                            'target': v2.name,
                            'id': f'{edge_pair[0]}-{edge_pair[1]}-{i}',
                            'oriented': False,
                            'arrow_shape': 'none',
                        }
                    })
                added_edges.add(edge_pair)

    # Chip indicator nodes around each vertex
    for vertex_obj, chips in divisor.degrees.items():
        if chips != 0:
            pos = positions.get(vertex_obj.name, (400, 300))
            elements.extend(_chip_indicator_elements(vertex_obj.name, pos[0], pos[1], chips))

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
        'selector': 'node', # Default node style
        'style': {
            'label': 'data(label)',
            'background-color': '#D3D3D3', # Light gray default
            'color': '#000000',
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
        'selector': 'node[divisor_sign = "zero"]',
        'style': {
            'background-color': '#D3D3D3', # Gray for zero chips
            'text-outline-color': '#D3D3D3',
            'color': '#000000'
        }
    },
    {
        'selector': 'node[divisor_sign = "positive"]',
        'style': {
            'background-color': '#28a745', # Green for positive chips
            'text-outline-color': '#28a745',
            'color': '#ffffff'
        }
    },
    {
        'selector': 'node[divisor_sign = "negative"]',
        'style': {
            'background-color': '#dc3545', # Red for negative chips
            'text-outline-color': '#dc3545',
            'color': '#ffffff'
        }
    },
    {
        'selector': 'node[divisor_sign = "non-negative"]', # backward compatibility
        'style': {
            'background-color': '#28a745',
            'text-outline-color': '#28a745',
            'color': '#ffffff'
        }
    },
    # Chip indicator dots
    {
        'selector': 'node[chip_type]',
        'style': {
            'width': 'data(chip_size)',
            'height': 'data(chip_size)',
            'label': '',
            'text-outline-width': 0,
            'border-width': 1,
            'border-color': '#000000',
            'z-index': 10,
        }
    },
    {
        'selector': 'node[chip_type = "positive_chip"]',
        'style': {
            'background-color': '#28a745',
        }
    },
    {
        'selector': 'node[chip_type = "negative_chip"]',
        'style': {
            'background-color': '#dc3545',
        }
    },
    {
        'selector': 'node:selected',
        'style': {
            # Semi-transparent gray halo — visible on any background color
            'overlay-color':   '#555',
            'overlay-opacity': 0.25,
            'overlay-padding': '7px',
        }
    },
    {
        'selector': 'node[chip_type = "traveling_chip"]',
        'style': {
            'background-color': '#28a745',  # green — chips in transit are positive
            'opacity': 0.85,
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

COSE_LAYOUT = {
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


def visualize(cf_object: any):
    """ Creates and runs a Dash app to visualize a chip-firing object.

    Args:
        cf_object: The chip-firing object (CFGraph, CFDivisor, CFOrientation).

    Raises:
        TypeError: If the object type is not supported for visualization.
    """
    title = "Chip-Firing Visualization"
    elements = []
    layout = COSE_LAYOUT

    if isinstance(cf_object, CFGraph):
        title = "Graph Visualization"
        elements = _graph_to_cytoscape_elements(cf_object)
        for el in elements:
            if 'source' in el.get('data', {}):
                el['data']['arrow_shape'] = 'none'
        initial_graph = cf_object
        initial_mode  = 'graph'
    elif isinstance(cf_object, CFDivisor):
        title = "Divisor Visualization"
        elements = _divisor_to_cytoscape_elements(cf_object)
        layout = {'name': 'preset', 'padding': 30}
        initial_graph = cf_object.graph
        initial_mode  = 'divisor'
    elif isinstance(cf_object, CFOrientation):
        title = "Orientation Visualization"
        elements = _orientation_to_cytoscape_elements(cf_object)
        initial_graph = cf_object.graph
        initial_mode  = 'orientation'
    else:
        raise TypeError(f"Visualization not supported for object of type {type(cf_object).__name__}")

    _assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
    app = Dash(__name__, assets_folder=_assets)

    _btn_base = {
        'padding': '5px 14px', 'font-size': '13px',
        'cursor': 'pointer', 'border': '1px solid #aaa',
    }
    _inp = {
        'padding': '4px 6px', 'font-size': '13px',
        'border': '1px solid #aaa', 'border-radius': '3px',
        'vertical-align': 'middle',
    }
    _show = {'display': 'block'}
    _hide = {'display': 'none'}

    # ── Graph-only controls ───────────────────────────────────────────────
    graph_only_controls = html.Div(
        id='graph-only-controls',
        children=[
            html.Button(
                'Visualize as Divisor (zero chips)',
                id='to-zero-divisor-btn',
                title='Switch to divisor visualization with 0 chips on every vertex',
                style={**_btn_base, 'border-radius': '4px', 'margin-right': '8px',
                       'vertical-align': 'middle'},
            ),
            html.Button(
                'Visualize as Canonical Divisor',
                id='to-canonical-divisor-btn',
                title='Switch to divisor visualization with K(v) = deg(v) - 2',
                style={**_btn_base, 'border-radius': '4px', 'margin-right': '8px',
                       'vertical-align': 'middle'},
            ),
        ],
        style={**(_show if initial_mode == 'graph' else _hide), 'margin': '6px 8px'},
    )

    # ── Divisor controls (graph selector + fire/burn toolbar) ─────────────
    divisor_controls = html.Div(
        id='divisor-controls',
        children=[
            # Graph selector row
            html.Div(
                [
                    html.Span('Load graph:', style={'font-size': '13px', 'color': '#333',
                                                    'vertical-align': 'middle',
                                                    'margin-right': '6px'}),
                    html.Div(
                        dcc.Dropdown(
                            id='graph-selector-dropdown',
                            options=[
                                {'label': 'Tetrahedron (K₄)',    'value': 'tetrahedron'},
                                {'label': 'Cube',                'value': 'cube'},
                                {'label': 'Octahedron (K₂,₂,₂)', 'value': 'octahedron'},
                                {'label': 'Dodecahedron',        'value': 'dodecahedron'},
                                {'label': 'Icosahedron',         'value': 'icosahedron'},
                                {'label': 'Complete graph Kₙ',   'value': 'complete'},
                                {'label': 'Chain of cycles',     'value': 'chain'},
                            ],
                            placeholder='Select graph…',
                            clearable=False,
                            style={'font-size': '13px'},
                        ),
                        style={'display': 'inline-block', 'width': '220px',
                               'vertical-align': 'middle', 'margin-right': '8px'},
                    ),
                    html.Div(
                        [html.Span('n =', style={'font-size': '13px', 'margin-right': '4px',
                                                  'vertical-align': 'middle'}),
                         dcc.Input(id='param-n', type='number', value=5, min=2, max=50,
                                   style={**_inp, 'width': '52px'})],
                        id='param-n-container',
                        style={'display': 'none', 'vertical-align': 'middle',
                               'margin-right': '8px'},
                    ),
                    html.Div(
                        [html.Span('Cycle lengths:', style={'font-size': '13px',
                                                            'margin-right': '4px',
                                                            'vertical-align': 'middle'}),
                         dcc.Input(id='param-cycles', type='text', value='3,4,3',
                                   placeholder='e.g. 3,4,3',
                                   style={**_inp, 'width': '110px'})],
                        id='param-cycles-container',
                        style={'display': 'none', 'vertical-align': 'middle',
                               'margin-right': '8px'},
                    ),
                    html.Button('Load', id='load-graph-btn',
                                style={**_btn_base, 'border-radius': '4px',
                                       'vertical-align': 'middle', 'margin-right': '8px'}),
                    html.Span(id='graph-load-error',
                              style={'color': '#dc3545', 'font-size': '12px',
                                     'vertical-align': 'middle'}),
                ],
                style={'margin': '6px 8px'},
            ),
            html.Hr(style={'margin': '4px 0', 'border': 'none',
                           'border-top': '1px solid #ddd'}),
            # Fire / Burn toolbar
            html.Div(
                [
                    html.Span(
                        [
                            html.Button('Pan', id='mode-pan-btn',
                                        title='Drag to pan the viewport',
                                        style={**_btn_base, 'border-radius': '4px 0 0 4px',
                                               'background': '#333', 'color': '#fff',
                                               'font-weight': 'bold'}),
                            html.Button('Select', id='mode-select-btn',
                                        title='Drag to rubber-band select vertices',
                                        style={**_btn_base, 'border-radius': '0 4px 4px 0',
                                               'background': '#f0f0f0', 'color': '#333',
                                               'font-weight': 'normal'}),
                        ],
                        style={'margin-right': '16px', 'vertical-align': 'middle'},
                    ),
                    html.Button('Fire Selected', id='fire-selected-btn',
                                title='Fire all selected vertices (or press Enter)',
                                style={**_btn_base, 'border-radius': '4px',
                                       'margin-right': '8px', 'vertical-align': 'middle'}),
                    html.Button('Zero Divisor', id='zero-divisor-btn',
                                title='Reset all chips to 0',
                                style={**_btn_base, 'border-radius': '4px',
                                       'margin-right': '8px', 'vertical-align': 'middle'}),
                    html.Button('Canonical Divisor', id='canonical-divisor-btn',
                                title='Reset chips to K(v) = deg(v) − 2 on current graph',
                                style={**_btn_base, 'border-radius': '4px',
                                       'margin-right': '16px', 'vertical-align': 'middle'}),
                    html.Span('│', style={'color': '#ccc', 'margin-right': '16px',
                                          'vertical-align': 'middle', 'font-size': '18px'}),
                    html.Button("Burn (Dhar's)", id='burn-btn',
                                title="Select one vertex as q, then run Dhar's algorithm",
                                style={**_btn_base, 'border-radius': '4px',
                                       'margin-right': '8px', 'vertical-align': 'middle'}),
                    html.Button('Clear Burn', id='clear-burn-btn',
                                title='Clear Dhar burn decorations',
                                style={**_btn_base, 'border-radius': '4px',
                                       'margin-right': '8px', 'vertical-align': 'middle'}),
                    html.Span('Select one vertex as q, then click or press B',
                              style={'color': '#555', 'font-size': '12px',
                                     'vertical-align': 'middle'}),
                ],
                style={'margin': '6px 8px'},
            ),
            html.Div(id='burn-result',
                     style={'margin': '4px 8px', 'font-size': '13px',
                            'min-height': '18px'}),
        ],
        style=_show if initial_mode == 'divisor' else _hide,
    )

    app.layout = html.Div([
        html.H1("Chip-Firing Visualizer"),
        html.H2(title),
        # Hidden mode indicator read by chip_drag.js
        html.Div(id='viz-mode', children=initial_mode, style=_hide),
        # Hidden store tracking which graph is currently displayed
        dcc.Store(id='current-graph-spec', data={'type': 'initial'}),
        graph_only_controls,
        divisor_controls,
        cyto.Cytoscape(
            id='cytoscape-graph',
            elements=elements,
            style={'width': '100%', 'height': '600px'},
            layout=layout,
            stylesheet=BASE_STYLESHEET,
        ),
    ])

    # ── Helpers shared by multiple callbacks ─────────────────────────────
    def _build_graph(graph_type, param_n, param_cycles):
        """Return a CFGraph from selector values; raises on bad input."""
        if   graph_type == 'tetrahedron': return tetrahedron()
        elif graph_type == 'cube':        return cube()
        elif graph_type == 'octahedron':  return octahedron()
        elif graph_type == 'dodecahedron':return dodecahedron()
        elif graph_type == 'icosahedron': return icosahedron()
        elif graph_type == 'complete':
            return complete_graph(int(param_n) if param_n else 5)
        elif graph_type == 'chain':
            return basicChain([int(x.strip()) for x in str(param_cycles).split(',')])
        raise ValueError(f'Unknown graph type: {graph_type}')

    _preset_layout = {'name': 'preset', 'padding': 30}

    # ── Callbacks ────────────────────────────────────────────────────────

    # Show/hide Kₙ / chain parameter inputs
    @app.callback(
        Output('param-n-container',      'style'),
        Output('param-cycles-container', 'style'),
        Input('graph-selector-dropdown', 'value'),
    )
    def toggle_params(graph_type):
        show_il = {'display': 'inline-block', 'vertical-align': 'middle',
                   'margin-right': '8px'}
        if graph_type == 'complete': return show_il, _hide
        if graph_type == 'chain':   return _hide, show_il
        return _hide, _hide

    # Load graph from selector (divisor-mode button)
    @app.callback(
        Output('cytoscape-graph',  'elements'),
        Output('cytoscape-graph',  'layout'),
        Output('graph-load-error', 'children'),
        Output('current-graph-spec', 'data'),
        Input('load-graph-btn', 'n_clicks'),
        State('graph-selector-dropdown', 'value'),
        State('param-n',      'value'),
        State('param-cycles', 'value'),
        prevent_initial_call=True,
    )
    def load_graph(_, graph_type, param_n, param_cycles):
        if not graph_type:
            return no_update, no_update, 'Select a graph type first.', no_update
        try:
            graph = _build_graph(graph_type, param_n, param_cycles)
            spec  = {'type': graph_type,
                     **(({'n': int(param_n)} if param_n else {}) if graph_type == 'complete' else {}),
                     **(({'lengths': [int(x.strip()) for x in str(param_cycles).split(',')]})
                        if graph_type == 'chain' else {})}
            return (_divisor_to_cytoscape_elements(_make_zero_divisor(graph)),
                    _preset_layout, '', spec)
        except Exception as exc:
            return no_update, no_update, str(exc), no_update

    # "Visualize as Divisor" buttons (graph mode → divisor mode)
    @app.callback(
        Output('cytoscape-graph',    'elements', allow_duplicate=True),
        Output('cytoscape-graph',    'layout',   allow_duplicate=True),
        Output('viz-mode',           'children'),
        Output('graph-only-controls','style'),
        Output('divisor-controls',   'style'),
        Input('to-zero-divisor-btn',      'n_clicks'),
        Input('to-canonical-divisor-btn', 'n_clicks'),
        State('current-graph-spec', 'data'),
        prevent_initial_call=True,
    )
    def switch_to_divisor(_z, _c, spec):
        graph = _graph_from_spec(spec, initial_graph)
        divisor = (_make_canonical_divisor(graph)
                   if ctx.triggered_id == 'to-canonical-divisor-btn'
                   else _make_zero_divisor(graph))
        return (_divisor_to_cytoscape_elements(divisor),
                _preset_layout, 'divisor', _hide, _show)

    # "Zero / Canonical Divisor" buttons (already in divisor mode)
    @app.callback(
        Output('cytoscape-graph', 'elements', allow_duplicate=True),
        Output('cytoscape-graph', 'layout',   allow_duplicate=True),
        Input('zero-divisor-btn',      'n_clicks'),
        Input('canonical-divisor-btn', 'n_clicks'),
        State('current-graph-spec', 'data'),
        prevent_initial_call=True,
    )
    def set_special_divisor(_z, _c, spec):
        graph = _graph_from_spec(spec, initial_graph)
        divisor = (_make_canonical_divisor(graph)
                   if ctx.triggered_id == 'canonical-divisor-btn'
                   else _make_zero_divisor(graph))
        return (_divisor_to_cytoscape_elements(divisor), _preset_layout)

    # Clientside: when viz-mode changes to 'divisor', re-init chip handlers in JS
    app.clientside_callback(
        """
        function(mode) {
            if (mode === 'divisor' && window._reinitChipHandlers) {
                window._reinitChipHandlers();
            }
            return '';
        }
        """,
        Output('viz-mode', 'title'),   # dummy output (title attr is harmless)
        Input('viz-mode', 'children'),
    )

    app.run(debug=True, use_reloader=False)
