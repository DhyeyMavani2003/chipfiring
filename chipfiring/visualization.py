"""
Visualization utilities for the chip-firing game.
"""

import networkx as nx  # type: ignore
import matplotlib.pyplot as plt
from matplotlib import cm
from typing import Dict, Optional, Tuple, Any, List
from .graph import Graph, Vertex, Direction # Import Direction
from .divisor import Divisor


def _get_graph_vertices(G: Graph) -> List[Vertex]:
    """Helper to get a sorted list of vertices from the graph."""
    return sorted(G._adjacency.keys())

def _to_networkx_graph(G: Graph) -> nx.MultiGraph:
    """Convert our Graph instance to an undirected networkx MultiGraph."""
    nx_G = nx.MultiGraph() # Use MultiGraph for multiple edges
    vertices = _get_graph_vertices(G)
    nx_G.add_nodes_from(vertices)

    # Add edges based on adjacency, avoiding double counting for undirected
    seen_edges = set()
    for v1 in vertices:
        for v2, count in G._adjacency.get(v1, {}).items():
            # Ensure v1 < v2 to process each edge pair once
            if v1 < v2:
                for _ in range(count):
                     nx_G.add_edge(v1, v2)

    return nx_G

def _to_networkx_digraph(G: Graph) -> nx.MultiDiGraph:
    """Convert our Graph instance to a directed networkx MultiDiGraph based on orientation."""
    nx_G = nx.MultiDiGraph() # Use MultiDiGraph for directed edges
    vertices = _get_graph_vertices(G)
    nx_G.add_nodes_from(vertices)

    # Iterate through all potential edges and add based on orientation
    for v1 in vertices:
        for v2, count in G._adjacency.get(v1, {}).items():
            if count > 0: # Only consider existing edges
                direction = G.get_edge_direction(v1, v2)
                if direction == Direction.OUTGOING:
                    for _ in range(count):
                        nx_G.add_edge(v1, v2)
                elif direction == Direction.UNDIRECTED:
                     # Represent undirected edge as two directed edges or handle differently?
                     # For now, add edges in both directions if undirected in a DiGraph context
                     # This might visually look like an undirected edge if arrows aren't distinct
                     # Or, could only add v1->v2 if v1 < v2 for undirected
                     if v1 < v2:
                         for _ in range(count):
                              nx_G.add_edge(v1, v2)
                              nx_G.add_edge(v2, v1)
                # INCOMING edges are handled when iterating from the other vertex (v2)
                
    return nx_G


def draw_graph(
    G: Graph,
    D: Optional[Divisor] = None,
    title: Optional[str] = None,
    pos: Optional[Dict[Vertex, Tuple[float, float]]] = None,
    node_color: str = "lightblue",
    edge_color: str = "gray",
    node_size: int = 1000,
    font_size: int = 12,
    use_orientation: bool = False, # New flag to control drawing direction
    **kwargs: Any # Allow passing extra args to nx.draw
) -> Tuple[plt.Figure, plt.Axes]:
    """Draw a graph with optional divisor values and orientation.

    Args:
        G: The graph to draw.
        D: Optional divisor to visualize.
        title: Optional title for the plot.
        pos: Optional dictionary of vertex positions.
        node_color: Default color for nodes (if D is None).
        edge_color: Default color for edges.
        node_size: Size of nodes.
        font_size: Size of font for labels.
        use_orientation: If True, draw directed edges based on G._orientation.
        kwargs: Additional arguments passed to networkx drawing functions.

    Returns:
        Tuple of (figure, axes) for further customization.
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    graph_vertices = _get_graph_vertices(G)

    # Choose graph type based on orientation flag
    if use_orientation:
        nx_G = _to_networkx_digraph(G)
        is_directed = True
    else:
        nx_G = _to_networkx_graph(G)
        is_directed = False

    # Get vertex positions if not provided
    if pos is None:
        # spring_layout works for both Graph and DiGraph
        try:
             pos = nx.spring_layout(nx_G, seed=42) # Use seed for reproducibility
        except nx.NetworkXException: # Handle disconnected graphs if layout fails
             print("Warning: Graph layout failed (possibly disconnected?). Using random layout.")
             pos = nx.random_layout(nx_G, seed=42)

    # --- Draw Edges --- 
    # networkx draw functions handle MultiGraph/MultiDiGraph
    nx.draw_networkx_edges(nx_G, pos, edge_color=edge_color, ax=ax, arrows=is_directed, **kwargs)

    # --- Draw Nodes --- 
    node_colors_to_draw: Any = node_color # Default
    if D is not None:
        # Create a color map based on divisor values
        values = [D.values.get(v, 0) for v in graph_vertices] # Use .get for safety
        if values: # Ensure there are values to map
             vmin, vmax = min(values), max(values)
             # Handle case where all values are the same
             if vmin == vmax: 
                  vmin -= 1 
                  vmax += 1
             try: 
                  cmap = cm.get_cmap('RdYlBu')
                  norm = plt.Normalize(vmin=vmin, vmax=vmax)
                  node_colors_to_draw = [cmap(norm(val)) for val in values]
                  
                  sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
                  sm.set_array([])
                  plt.colorbar(sm, ax=ax, label="Divisor Value")
             except Exception as e:
                  print(f"Warning: Could not create color map for nodes: {e}")
                  node_colors_to_draw = node_color # Fallback
        else:
             node_colors_to_draw = node_color # Fallback if no values

    nx.draw_networkx_nodes(
        nx_G, pos, node_color=node_colors_to_draw, node_size=node_size, ax=ax, **kwargs
    )

    # --- Draw Labels --- 
    if D is not None:
        labels = {v: f"{v}\n{D.values.get(v, 0)}" for v in graph_vertices}
    else:
        labels = {v: str(v) for v in graph_vertices}

    nx.draw_networkx_labels(nx_G, pos, labels=labels, font_size=font_size, ax=ax, **kwargs)

    # Set title if provided
    if title:
        ax.set_title(title)

    # Remove axes
    ax.set_axis_off()
    plt.tight_layout()
    return fig, ax


def draw_game_state(
    game: Any, # Keep Any for now, assuming it has .graph and .current_divisor
    title: Optional[str] = None,
    pos: Optional[Dict[Vertex, Tuple[float, float]]] = None,
    node_size: int = 1000,
    font_size: int = 12,
    use_orientation: bool = False, # Pass orientation flag
    **kwargs: Any
) -> Tuple[plt.Figure, plt.Axes]:
    """Draw the current state of a chip-firing game (like DollarGame).

    Args:
        game: The game instance (must have .graph and .current_divisor).
        title: Optional title for the plot.
        pos: Optional dictionary of vertex positions.
        node_size: Size of nodes.
        font_size: Size of font for labels.
        use_orientation: If True, draw directed edges.
        kwargs: Additional arguments passed to draw_graph.

    Returns:
        Tuple of (figure, axes) for further customization.
    """
    if title is None:
        # Try to get degree, handle potential errors
        try:
            degree_str = f"Total: {game.current_divisor.degree()}"
        except AttributeError:
            degree_str = ""
        title = f"Game State {degree_str}".strip()
        
    # Ensure graph and divisor exist on the game object
    if not hasattr(game, 'graph') or not hasattr(game, 'current_divisor'):
         raise AttributeError("Game object must have 'graph' and 'current_divisor' attributes.")

    return draw_graph(
        game.graph,
        game.current_divisor,
        title=title,
        pos=pos,
        node_size=node_size,
        font_size=font_size,
        use_orientation=use_orientation,
        **kwargs
    )
