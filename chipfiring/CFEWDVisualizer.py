from __future__ import annotations
from dash import Dash, html, dcc, Input, Output, State, callback_context
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from .CFDivisor import CFDivisor
from .CFOrientation import CFOrientation
from .CFVisualizer import _graph_to_cytoscape_elements, BASE_STYLESHEET

class EWDVisualizer:
    def __init__(self):
        self.history = []

    def add_step(self, divisor: CFDivisor, orientation: CFOrientation, unburnt_vertices: set = None, firing_set: set = None, q: str = None, description: str = "", source_function: str = None):
        # Create copies of the divisor and orientation to avoid modifying the original objects
        divisor_copy = CFDivisor.from_dict(divisor.to_dict())
        orientation_copy = CFOrientation.from_dict(orientation.to_dict())
        
        self.history.append({
            "divisor": divisor_copy,
            "orientation": orientation_copy,
            "unburnt_vertices": set(unburnt_vertices) if unburnt_vertices is not None else set(),
            "firing_set": set(firing_set) if firing_set is not None else set(),
            "q": q,
            "description": description,
            "source_function": source_function
        })

    def visualize(self):
        if not self.history:
            print("No history to visualize.")
            return

        app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'])

        legend = dbc.Card([
            dbc.CardHeader(html.H4("Legend", className="mb-0")),
            dbc.CardBody([
                html.Div([html.Span(style={'backgroundColor': '#28a745', 'width': '20px', 'height': '20px', 'display': 'inline-block', 'marginRight': '10px', 'verticalAlign': 'middle', 'borderRadius': '50%'}), "Node with non-negative chips"]),
                html.Br(),
                html.Div([html.Span(style={'backgroundColor': '#dc3545', 'width': '20px', 'height': '20px', 'display': 'inline-block', 'marginRight': '10px', 'verticalAlign': 'middle', 'borderRadius': '50%'}), "Node with negative chips"]),
                html.Br(),
                html.Div([html.Span(style={'backgroundColor': '#6c757d', 'width': '20px', 'height': '20px', 'display': 'inline-block', 'marginRight': '10px', 'verticalAlign': 'middle', 'borderRadius': '50%'}), "Burnt node"]),
                html.Br(),
                html.Div([html.Span(style={'border': '5px solid #ffc107', 'width': '20px', 'height': '20px', 'display': 'inline-block', 'marginRight': '10px', 'verticalAlign': 'middle', 'borderRadius': '50%'}), "Node in firing set"]),
                html.Br(),
                html.Div([html.Span(style={'border': '3px solid #007bff', 'width': '20px', 'height': '20px', 'display': 'inline-block', 'marginRight': '10px', 'verticalAlign': 'middle', 'borderRadius': '50%'}), "Sink node (q)"]),
                html.Br(),
                html.Div([html.I(className='fa fa-long-arrow-right fa-2x', style={'color': '#555', 'marginRight': '10px', 'verticalAlign': 'middle'}), "Oriented edge"]),
            ])
        ], className="mt-3")

        app.layout = dbc.Container([
            html.H1("EWD Algorithm Visualization", className="my-4 text-center"),
            dcc.Store(id='step-store', data=0),
            dbc.Row([
                dbc.Col([
                    cyto.Cytoscape(
                        id='cytoscape-graph',
                        layout={'name': 'cose'},
                        style={'width': '100%', 'height': '70vh'},
                        stylesheet=BASE_STYLESHEET
                    )
                ], width=9),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H4("Description", className="mb-0")),
                        dbc.CardBody([
                            html.Div(id='step-description', style={'minHeight': '50px'}),
                        ])
                    ]),
                    legend
                ], width=3)
            ], align="center"),
            dbc.Row([
                dbc.Col(dbc.Button(html.I(className="fa fa-arrow-left"), id="prev-step-button", color="primary", n_clicks=0), width="auto"),
                dbc.Col(html.Div(id='step-counter', style={'textAlign': 'center', 'fontWeight': 'bold'}), width="auto"),
                dbc.Col(dbc.Button(html.I(className="fa fa-arrow-right"), id="next-step-button", color="primary", n_clicks=0), width="auto")
            ], justify="center", align="center", className="my-4")
        ], fluid=True)

        @app.callback(
            Output('step-store', 'data'),
            Input('prev-step-button', 'n_clicks'),
            Input('next-step-button', 'n_clicks'),
            State('step-store', 'data'),
            prevent_initial_call=True
        )
        def update_step_from_buttons(prev_clicks, next_clicks, current_step):
            ctx = callback_context
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if button_id == 'prev-step-button':
                return max(0, current_step - 1)
            elif button_id == 'next-step-button':
                return min(len(self.history) - 1, current_step + 1)
            return current_step

        @app.callback(
            Output('cytoscape-graph', 'elements'),
            Output('step-description', 'children'),
            Output('prev-step-button', 'disabled'),
            Output('next-step-button', 'disabled'),
            Output('step-counter', 'children'),
            Input('step-store', 'data')
        )
        def update_display(step_index):
            step_data = self.history[step_index]
            divisor = step_data["divisor"]
            orientation = step_data["orientation"]
            unburnt_vertices = step_data["unburnt_vertices"]
            firing_set = step_data["firing_set"]
            q = step_data["q"]
            description = step_data["description"]
            source_function = step_data.get("source_function")

            elements = self._get_elements(divisor, orientation, unburnt_vertices, firing_set, q)
            
            prev_disabled = step_index == 0
            next_disabled = step_index == len(self.history) - 1
            step_counter_text = f"Step {step_index + 1} of {len(self.history)}"

            description_content = []
            if source_function:
                description_content.append(html.H6(source_function, className="card-subtitle mb-2 text-muted"))
            description_content.append(html.P(description, className="card-text mb-0"))

            return elements, description_content, prev_disabled, next_disabled, step_counter_text

        app.run(debug=True)

    def _get_elements(self, divisor, orientation, unburnt_vertices, firing_set, q):
        elements = _graph_to_cytoscape_elements(divisor.graph)
        
        # Add divisor info
        for element in elements:
            if 'id' in element.get('data', {}) and 'label' in element.get('data', {}): # It's a node
                node_id = element['data']['id']

                if firing_set and node_id in [v.name if not isinstance(v, str) else v for v in firing_set]:
                    element['data']['is_in_firing_set'] = 'true'
                else:
                    element['data']['is_in_firing_set'] = 'false'

                vertex_obj = divisor.graph.get_vertex_by_name(node_id)
                if vertex_obj and vertex_obj in divisor.degrees:
                    chips = divisor.degrees[vertex_obj]
                    element['data']['label'] = f"{node_id}\n{chips}"
                    if chips < 0:
                        element['data']['divisor_sign'] = 'negative'
                    else:
                        element['data']['divisor_sign'] = 'non-negative'
                
                if node_id == q:
                    element['data']['is_q'] = 'true'
                else:
                    element['data']['is_q'] = 'false'

                # Unburnt vertices exist only during the burning phase.
                # A node is "burnt" if the unburnt_vertices set is not empty and the node is not in it.
                is_burning_phase = len(unburnt_vertices) > 0
                node_is_in_unburnt_set = node_id in [v if isinstance(v, str) else v.name for v in unburnt_vertices]
                
                if is_burning_phase and not node_is_in_unburnt_set:
                    element['data']['is_burnt'] = 'true'
                else:
                    element['data']['is_burnt'] = 'false'

        # Add orientation info
        if orientation:
            for element in elements:
                if 'source' in element.get('data', {}): # It's an edge
                    edge_id_parts = element['data']['id'].split('-')
                    id_v1_name = edge_id_parts[0]
                    id_v2_name = edge_id_parts[1]

                    oriented_pair = orientation.get_orientation(id_v1_name, id_v2_name)

                    if oriented_pair:
                        actual_source, actual_target = oriented_pair
                        element['data']['source'] = actual_source
                        element['data']['target'] = actual_target
                        element['data']['oriented'] = True
                        element['data']['arrow_shape'] = 'triangle'
                    else:
                        element['data']['oriented'] = False
                        element['data']['arrow_shape'] = 'none'
        return elements
