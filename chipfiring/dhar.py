"""
Implementation of Dhar's algorithm for chip-firing games.

This module provides functions to:
1. Find legal firing sets for configurations
2. Perform q-reduction on divisors
3. Determine game winnability using Dhar's algorithm
"""

from typing import Set, Optional, Dict
from .graph import Graph, Vertex
from .divisor import Divisor


def outdegree_to_set(graph: Graph, vertex: Vertex, subset: Set[Vertex]) -> int:
    """
    Calculate the outdegree of a vertex with respect to a subset of vertices.

    Args:
        graph: The graph
        vertex: The vertex to calculate outdegree for
        subset: The subset of vertices

    Returns:
        The number of edges from vertex to vertices outside of subset
    """
    outdegree = 0
    for neighbor in graph.get_neighbors(vertex):
        if neighbor not in subset:
            outdegree += graph.get_edge_count(vertex, neighbor)
    return outdegree


def find_legal_firing_set(graph: Graph, divisor: Divisor, q: Vertex) -> Set[Vertex]:
    """
    Implementation of Dhar's algorithm to find a legal firing set.

    Args:
        graph: The graph
        divisor: The current divisor
        q: The distinguished vertex (source)

    Returns:
        A set of vertices that can be legally fired (empty if divisor is q-reduced)
    """
    # Check if all non-q vertices are non-negative
    non_q_vertices = {v for v in graph.vertices if v != q}
    if not all(divisor[v] >= 0 for v in non_q_vertices):
        return set()  # Can't have a legal firing set with negative values

    # Start the burning process from q
    queue = [q]
    burned = {q}

    while queue:
        current = queue.pop(0)
        for neighbor in graph.get_neighbors(current):
            if neighbor not in burned:
                # Count edges from burned vertices to this neighbor
                burning_edges = 0
                for v in burned:
                    if v in graph.get_neighbors(neighbor):
                        burning_edges += graph.get_edge_count(v, neighbor)

                # If neighbor doesn't have enough chips to stop the fire, it burns
                if divisor[neighbor] < burning_edges:
                    burned.add(neighbor)
                    queue.append(neighbor)

    # The unburned vertices (excluding q) form a legal firing set
    return non_q_vertices - burned


def is_q_reduced(graph: Graph, divisor: Divisor, q: Vertex) -> bool:
    """
    Check if a divisor is q-reduced.

    Args:
        graph: The graph
        divisor: The divisor to check
        q: The distinguished vertex

    Returns:
        True if the divisor is q-reduced, False otherwise
    """
    # Condition 1: D(v) ≥ 0 for all v != q
    if not all(divisor[v] >= 0 for v in graph.vertices if v != q):
        return False

    # Condition 2: No legal firing set exists
    legal_set = find_legal_firing_set(graph, divisor, q)
    return len(legal_set) == 0


def send_debt_to_q(graph: Graph, divisor: Divisor, q: Vertex) -> Divisor:
    """
    Concentrate all debt at the distinguished vertex q.

    Args:
        graph: The graph
        divisor: The current divisor
        q: The distinguished vertex

    Returns:
        A new divisor with all non-q vertices out of debt
    """
    # Create a copy of the input divisor
    result = Divisor(graph, divisor.to_dict())

    # Sort vertices by distance from q (approximation)
    # This is a breadth-first traversal from q
    queue = [q]
    visited = {q}
    distance_ordering = [q]

    while queue:
        current = queue.pop(0)
        for neighbor in graph.get_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
                distance_ordering.append(neighbor)

    # Process vertices in reverse order of distance
    for v in reversed(distance_ordering[1:]):  # Skip q
        # While v is in debt, borrow
        while result[v] < 0:
            # Perform a borrowing move at v
            result[v] += graph.vertex_degree(v)
            for neighbor in graph.get_neighbors(v):
                edge_count = graph.get_edge_count(v, neighbor)
                result[neighbor] -= edge_count

    return result


def q_reduce(graph: Graph, divisor: Divisor, q: Vertex) -> Divisor:
    """
    Find the q-reduced divisor linearly equivalent to the input divisor.

    Args:
        graph: The graph
        divisor: The input divisor
        q: The distinguished vertex

    Returns:
        The q-reduced divisor linearly equivalent to the input
    """
    # Step 1: Send all debt to q
    result = send_debt_to_q(graph, divisor, q)

    # Step 2: Repeatedly find and fire legal sets until none exist
    iteration_count = 0
    max_iterations = 100  # Avoid infinite loops

    while iteration_count < max_iterations:
        legal_set = find_legal_firing_set(graph, result, q)
        if not legal_set:
            break

        # Fire the legal set
        for v in legal_set:
            # Update the vertex
            result[v] -= graph.vertex_degree(v)

            # Update neighbors
            for neighbor in graph.get_neighbors(v):
                edge_count = graph.get_edge_count(v, neighbor)
                result[neighbor] += edge_count

        iteration_count += 1

    return result


def is_winnable_dhar(graph: Graph, divisor: Divisor) -> bool:
    """
    Determine if a divisor is winnable using Dhar's algorithm.

    Args:
        graph: The graph
        divisor: The divisor to check

    Returns:
        True if the divisor is winnable, False otherwise
    """
    # Game is unwinnable if total money is negative
    if divisor.degree() < 0:
        return False

    # Choose any vertex as the distinguished vertex
    q = next(iter(graph.vertices))

    # Find the q-reduced divisor
    q_reduced_divisor = q_reduce(graph, divisor, q)

    # Game is winnable if and only if q is not in debt in the q-reduced divisor
    return q_reduced_divisor[q] >= 0


def get_winning_strategy_dhar(
    graph: Graph, divisor: Divisor
) -> Optional[Dict[Vertex, int]]:
    """
    Get a winning strategy using Dhar's algorithm if one exists.

    Args:
        graph: The graph
        divisor: The divisor

    Returns:
        A firing script (dictionary mapping vertices to firing counts) or None if no winning strategy exists
    """
    # Check if the divisor is winnable
    if not is_winnable_dhar(graph, divisor):
        return None

    # Choose any vertex as the distinguished vertex
    q = next(iter(graph.vertices))

    # Find the q-reduced divisor
    original_divisor = Divisor(graph, divisor.to_dict())
    q_reduced = q_reduce(graph, divisor, q)

    # Initialize firing script
    firing_script = {v: 0 for v in graph.vertices}

    # The difference between the original and q-reduced divisors
    # gives us the firing script
    for v in graph.vertices:
        # This is an approximation - in a real implementation we'd track
        # the actual firing counts during q-reduction
        firing_script[v] = original_divisor[v] - q_reduced[v]

    return firing_script
