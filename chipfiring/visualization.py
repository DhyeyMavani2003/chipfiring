"""
Visualization utilities for the chip-firing game.
"""

import networkx as nx  # type: ignore
import matplotlib.pyplot as plt
from matplotlib import cm
from typing import Dict, Optional, Tuple, Any
from .graph import Graph, Vertex
from .divisor import Divisor


def _to_networkx_graph(G: Graph) -> nx.Graph:
    """Convert our Graph instance to a networkx Graph.

    Args:
        G: Our Graph instance

    Returns:
        A networkx Graph instance
    """
    # Create a new networkx Graph
    nx_G = nx.Graph()

    # Add vertices
    for v in G.vertices:
        nx_G.add_node(v)

    # Add edges
    for edge, count in G.edges.items():
        for _ in range(count):
            nx_G.add_edge(edge.v1, edge.v2)

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
) -> Tuple[plt.Figure, plt.Axes]:
    """Draw a graph with optional divisor values.

    Args:
        G: The graph to draw.
        D: Optional divisor to visualize.
        title: Optional title for the plot.
        pos: Optional dictionary of vertex positions.
        node_color: Color for nodes.
        edge_color: Color for edges.
        node_size: Size of nodes.
        font_size: Size of font for labels.

    Returns:
        Tuple of (figure, axes) for further customization.
    """
    # Create figure and axes
    fig, ax = plt.subplots(figsize=(10, 8))

    # Convert our Graph to networkx Graph
    nx_G = _to_networkx_graph(G)

    # Get vertex positions if not provided
    if pos is None:
        pos = nx.spring_layout(nx_G)

    # Draw edges
    nx.draw_networkx_edges(nx_G, pos, edge_color=edge_color, ax=ax)

    # Draw nodes
    if D is not None:
        # Create a color map based on divisor values
        values = [D[v] for v in G.vertices]
        vmin, vmax = min(values), max(values)
        cmap = cm.get_cmap('RdYlBu')
        sm = plt.cm.ScalarMappable(
            cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax)
        )
        sm.set_array([])

        # Draw nodes with colors based on divisor values
        nx.draw_networkx_nodes(
            nx_G, pos, node_color=values, cmap=cmap, node_size=node_size, ax=ax
        )

        # Add colorbar
        plt.colorbar(sm, ax=ax, label="Wealth")

        # Add vertex labels with divisor values
        labels = {v: f"{v}\n{D[v]}" for v in G.vertices}
    else:
        # Draw nodes with uniform color
        nx.draw_networkx_nodes(
            nx_G, pos, node_color=node_color, node_size=node_size, ax=ax
        )

        # Add vertex labels
        labels = {v: str(v) for v in G.vertices}

    # Draw labels
    nx.draw_networkx_labels(nx_G, pos, labels, font_size=font_size, ax=ax)

    # Set title if provided
    if title:
        ax.set_title(title)

    # Remove axes
    ax.set_axis_off()

    return fig, ax


def draw_game_state(
    game: Any,
    title: Optional[str] = None,
    pos: Optional[Dict[Vertex, Tuple[float, float]]] = None,
    node_size: int = 1000,
    font_size: int = 12,
) -> Tuple[plt.Figure, plt.Axes]:
    """Draw the current state of the dollar game.

    Args:
        game: The DollarGame instance.
        title: Optional title for the plot.
        pos: Optional dictionary of vertex positions.
        node_size: Size of nodes.
        font_size: Size of font for labels.

    Returns:
        Tuple of (figure, axes) for further customization.
    """
    if title is None:
        title = f"Dollar Game State (Total: {game.get_degree()})"
    return draw_graph(
        game.graph,
        game.current_divisor,
        title=title,
        pos=pos,
        node_size=node_size,
        font_size=font_size,
    )
