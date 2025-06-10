"""
Combinatorial tools for chip firing and gonality studies.

This module provides functions for parking functions, independent sets,
treewidth calculations, and scramble numbers as mentioned in the academic literature.
"""
from __future__ import annotations
from typing import List, Set, Dict, Optional
import networkx as nx
from .CFGraph import CFGraph


def is_parking_function(sequence: List[int], n: Optional[int] = None) -> bool:
    """
    Check if a sequence is a parking function.
    
    A parking function of length n is a sequence (a1, a2, ..., an) where
    ai ∈ {1, 2, ..., n} such that if we sort the sequence in non-decreasing order
    to get (b1, b2, ..., bn), then bi ≤ i for all i.
    
    Args:
        sequence: The sequence to test
        n: Length constraint (if None, uses len(sequence))
        
    Returns:
        bool: True if sequence is a parking function
        
    Examples:
        >>> is_parking_function([1, 1, 2])
        True
        >>> is_parking_function([1, 3, 2])
        False
        >>> is_parking_function([2, 1, 1])
        True
    """
    if not sequence:
        return True
    
    if n is None:
        n = len(sequence)
    
    if len(sequence) != n:
        return False
    
    # Check that all elements are in range [1, n]
    if not all(1 <= x <= n for x in sequence):
        return False
    
    # Sort and check parking condition
    sorted_seq = sorted(sequence)
    return all(sorted_seq[i] <= i + 1 for i in range(n))


def generate_parking_functions(n: int) -> List[List[int]]:
    """
    Generate all parking functions of length n.
    
    Args:
        n: Length of parking functions to generate
        
    Returns:
        List[List[int]]: All parking functions of length n
        
    Examples:
        >>> funcs = generate_parking_functions(2)
        >>> len(funcs)
        3
        >>> sorted(funcs)
        [[1, 1], [1, 2], [2, 1]]
    """
    if n <= 0:
        return []
    
    parking_functions = []
    
    # Generate all possible sequences
    def backtrack(current_seq: List[int]):
        if len(current_seq) == n:
            if is_parking_function(current_seq, n):
                parking_functions.append(current_seq[:])
            return
        
        for i in range(1, n + 1):
            current_seq.append(i)
            backtrack(current_seq)
            current_seq.pop()
    
    backtrack([])
    return parking_functions


def parking_function_count(n: int) -> int:
    """
    Return the number of parking functions of length n.
    
    The number of parking functions of length n is (n+1)^(n-1).
    
    Args:
        n: Length of parking functions
        
    Returns:
        int: Number of parking functions of length n
        
    Examples:
        >>> parking_function_count(1)
        1
        >>> parking_function_count(2)
        3
        >>> parking_function_count(3)
        16
    """
    if n <= 0:
        return 0
    return (n + 1) ** (n - 1)


def is_connected(graph: CFGraph) -> bool:
    """
    Check if a graph is connected.
    
    Args:
        graph: The graph to check
        
    Returns:
        bool: True if graph is connected
    """
    if len(graph.vertices) <= 1:
        return True
    
    # DFS to check connectivity
    start_vertex = next(iter(graph.vertices))
    visited = set()
    stack = [start_vertex]
    
    while stack:
        vertex = stack.pop()
        if vertex in visited:
            continue
        
        visited.add(vertex)
        
        # Add neighbors to stack
        for neighbor in graph.graph[vertex]:
            if neighbor not in visited:
                stack.append(neighbor)
    
    return len(visited) == len(graph.vertices)


def maximal_independent_sets(graph: CFGraph) -> List[Set[str]]:
    """
    Find all maximal independent sets in a graph.
    
    An independent set is a set of vertices with no edges between them.
    A maximal independent set cannot be extended by adding another vertex.
    
    Args:
        graph: The graph to analyze
        
    Returns:
        List[Set[str]]: List of maximal independent sets (vertex names)
        
    Examples:
        >>> vertices = {"0", "1", "2"}
        >>> edges = [("0", "1", 1)]
        >>> graph = CFGraph(vertices, edges)
        >>> mis = maximal_independent_sets(graph)
        >>> len(mis) >= 1
        True
    """
    # Handle empty graph case
    if len(graph.vertices) == 0:
        return [set()]  # Empty set is the only maximal independent set
    
    # Convert to NetworkX for efficient computation
    nx_graph = nx.Graph()
    for vertex in graph.vertices:
        nx_graph.add_node(vertex.name)
    
    # Add edges from CFGraph's adjacency representation
    for v1 in graph.vertices:
        for v2, valence in graph.graph[v1].items():
            if v1.name < v2.name:  # Avoid duplicate edges in undirected graph
                nx_graph.add_edge(v1.name, v2.name)
    
    # Find all maximal independent sets
    mis_list = []
    for mis in nx.find_cliques(nx.complement(nx_graph)):
        mis_list.append(set(mis))
    
    return mis_list


def independence_number(graph: CFGraph) -> int:
    """
    Compute the independence number (size of largest independent set).
    
    Args:
        graph: The graph to analyze
        
    Returns:
        int: The independence number
        
    Examples:
        >>> vertices = {"0", "1", "2"}
        >>> edges = [("0", "1", 1)]
        >>> graph = CFGraph(vertices, edges)
        >>> independence_number(graph) >= 1
        True
    """
    mis_list = maximal_independent_sets(graph)
    if not mis_list:
        return 0
    return max(len(mis) for mis in mis_list)


def minimum_degree(graph: CFGraph) -> int:
    """
    Compute the minimum degree of a graph.
    
    This provides a simple lower bound on treewidth and gonality:
    δ(G) ≤ tw(G) ≤ gon(G)
    
    Args:
        graph: The graph to analyze
        
    Returns:
        int: The minimum degree
        
    Examples:
        >>> vertices = {"0", "1", "2"}
        >>> edges = [("0", "1", 1), ("1", "2", 1), ("0", "2", 1)]
        >>> graph = CFGraph(vertices, edges)
        >>> minimum_degree(graph)
        2
    """
    if len(graph.vertices) == 0:
        return 0
    
    return min(graph.get_valence(v.name) for v in graph.vertices)


def maximum_degree(graph: CFGraph) -> int:
    """
    Compute the maximum degree of a graph.
    
    Args:
        graph: The graph to analyze
        
    Returns:
        int: The maximum degree
        
    Examples:
        >>> vertices = {"0", "1", "2", "3"}
        >>> edges = [("0", "1", 1), ("1", "2", 1), ("2", "3", 1)]
        >>> graph = CFGraph(vertices, edges)
        >>> maximum_degree(graph)
        2
    """
    if len(graph.vertices) == 0:
        return 0
    
    return max(graph.get_valence(v.name) for v in graph.vertices)


def is_bipartite(graph: CFGraph) -> bool:
    """
    Check if a graph is bipartite.
    
    Args:
        graph: The graph to check
        
    Returns:
        bool: True if the graph is bipartite
        
    Examples:
        >>> vertices = {"0", "1", "2", "3"}
        >>> edges = [("0", "2", 1), ("0", "3", 1), ("1", "2", 1), ("1", "3", 1)]
        >>> graph = CFGraph(vertices, edges)
        >>> is_bipartite(graph)
        True
    """
    if len(graph.vertices) <= 1:
        return True
    
    # Convert to NetworkX for bipartite testing
    nx_graph = nx.Graph()
    for vertex in graph.vertices:
        nx_graph.add_node(vertex.name)
    
    for v1 in graph.vertices:
        for v2, valence in graph.graph[v1].items():
            if v1.name < v2.name:  # Avoid duplicate edges
                nx_graph.add_edge(v1.name, v2.name)
    
    return nx.is_bipartite(nx_graph)


def bramble_order_lower_bound(graph: CFGraph) -> int:
    """
    Compute a lower bound on the maximum bramble order.
    
    Based on the theory from "Chip-firing on the Platonic solids",
    this provides a lower bound on treewidth and thus gonality.
    
    Args:
        graph: The graph to analyze
        
    Returns:
        int: Lower bound on maximum bramble order
        
    Examples:
        >>> vertices = {"0", "1", "2"}
        >>> edges = [("0", "1", 1), ("1", "2", 1), ("0", "2", 1)]
        >>> graph = CFGraph(vertices, edges)
        >>> bramble_order_lower_bound(graph) >= 1
        True
    """
    n = len(graph.vertices)
    if n <= 1:
        return 1
    
    # For complete graphs K_n, bramble order is n
    expected_edges = n * (n - 1) // 2
    actual_edges = sum(1 for v1 in graph.vertices 
                      for v2, valence in graph.graph[v1].items() 
                      if v1.name < v2.name)
    
    if actual_edges == expected_edges:
        return n  # Complete graph has bramble order n
    
    # For bipartite graphs, use minimum degree + 1
    if is_bipartite(graph):
        return minimum_degree(graph) + 1
    
    # General lower bound based on minimum degree
    return minimum_degree(graph) + 1


def complete_multipartite_gonality(partition_sizes: List[int]) -> int:
    """
    Compute the exact gonality of a complete multipartite graph K_{n1,n2,...,nk}.
    
    For k >= 2 partitions: gon(K_{n1,n2,...,nk}) = n - min(ni) where min(ni) is the smallest part.
    For k = 1 partition: gon(K_n) = n - 1 (complete graph gonality).
    
    Args:
        partition_sizes: List of partition sizes
        
    Returns:
        int: The exact gonality
        
    Examples:
        >>> complete_multipartite_gonality([2, 2, 2])  # Octahedron K_{2,2,2}
        4
        >>> complete_multipartite_gonality([3, 4])  # K_{3,4}
        4
        >>> complete_multipartite_gonality([5])  # K_5 (complete graph)
        4
    """
    if not partition_sizes:
        return 0
    
    n = sum(partition_sizes)
    
    # Special case: single partition = complete graph K_n
    if len(partition_sizes) == 1:
        return n - 1
    
    # General case: complete multipartite with k >= 2 partitions
    nk = min(partition_sizes)  # Use smallest part
    return n - nk


def octahedron_independence_number() -> int:
    """
    Compute the independence number of the octahedron (K_{2,2,2}).
    
    As proven in the theory, the octahedron has independence number 2.
    
    Returns:
        int: The independence number (2)
    """
    return 2


def octahedron_bramble_construction() -> Dict[str, any]:
    """
    Construct the bramble of order 5 on the octahedron as described in the theory.
    
    This bramble proves that the treewidth of the octahedron is at least 4.
    
    Returns:
        Dict[str, any]: Information about the bramble construction
    """
    # Label vertices u1, u2, v1, v2, w1, w2 where a vertex is connected 
    # only to those vertices with a different letter label
    bramble_sets = [
        {"u1"},
        {"v1"}, 
        {"w1"},
        {"u2", "v2"},
        {"u2", "w2"},
        {"v2", "w2"}
    ]
    
    # Any hitting set needs u1, v1, w1 (singleton sets) plus at least 2 of {u2, v2, w2}
    min_hitting_set_size = 5
    
    return {
        'bramble_sets': bramble_sets,
        'order': min_hitting_set_size,
        'separators': min_hitting_set_size - 1,
        'treewidth_lower_bound': min_hitting_set_size - 1,
        'description': 'Bramble of order 5 on octahedron K_{2,2,2} proving treewidth >= 4',
        'vertex_labeling': {
            'u1': 'v0', 'u2': 'v1',  # Group 1
            'v1': 'v2', 'v2': 'v3',  # Group 2
            'w1': 'v4', 'w2': 'v5'   # Group 3
        }
    }


def treewidth_upper_bound(graph: CFGraph) -> int:
    """
    Compute an upper bound for the treewidth of a graph.
    
    This uses a simple greedy elimination ordering to get an upper bound.
    The actual treewidth may be smaller.
    
    Args:
        graph: The graph to analyze
        
    Returns:
        int: Upper bound on treewidth
        
    Examples:
        >>> vertices = {"0", "1", "2", "3"}
        >>> edges = [("0", "1", 1), ("1", "2", 1), ("2", "3", 1), ("3", "0", 1)]
        >>> graph = CFGraph(vertices, edges)
        >>> treewidth_upper_bound(graph) >= 1
        True
    """
    if len(graph.vertices) <= 1:
        return 0
    
    # Convert to NetworkX
    nx_graph = nx.Graph()
    for vertex in graph.vertices:
        nx_graph.add_node(vertex.name)
    
    # Add edges from CFGraph's adjacency representation
    for v1 in graph.vertices:
        for v2, valence in graph.graph[v1].items():
            if v1.name < v2.name:  # Avoid duplicate edges in undirected graph
                nx_graph.add_edge(v1.name, v2.name)
    
    # Use minimum degree elimination heuristic
    G = nx_graph.copy()
    max_clique_size = 0
    
    while G.nodes():
        # Find vertex with minimum degree
        min_degree_vertex = min(G.nodes(), key=lambda v: G.degree(v))
        
        # Get neighbors
        neighbors = list(G.neighbors(min_degree_vertex))
        
        # Make neighbors form a clique
        for i in range(len(neighbors)):
            for j in range(i + 1, len(neighbors)):
                if not G.has_edge(neighbors[i], neighbors[j]):
                    G.add_edge(neighbors[i], neighbors[j])
        
        # Update max clique size
        max_clique_size = max(max_clique_size, len(neighbors) + 1)
        
        # Remove vertex
        G.remove_node(min_degree_vertex)
    
    return max_clique_size - 1


def scramble_number_upper_bound(graph: CFGraph) -> int:
    """
    Compute an upper bound for the scramble number of a graph.
    
    The scramble number is related to gonality and chip firing dynamics.
    This provides a theoretical upper bound based on graph structure.
    
    Args:
        graph: The graph to analyze
        
    Returns:
        int: Upper bound on scramble number
        
    Examples:
        >>> vertices = {"0", "1", "2"}
        >>> edges = [("0", "1", 1), ("1", "2", 1)]
        >>> graph = CFGraph(vertices, edges)
        >>> scramble_number_upper_bound(graph) >= 1
        True
    """
    n = len(graph.vertices)
    if n <= 1:
        return 0
    
    # Upper bound based on independence number and treewidth
    alpha = independence_number(graph)
    tw_bound = treewidth_upper_bound(graph)
    
    # Theoretical upper bound: min(n-1, α + tw + 1)
    return min(n - 1, alpha + tw_bound + 1)


def genus_upper_bound(graph: CFGraph) -> int:
    """
    Compute an upper bound for the genus of a graph.
    
    The genus is related to gonality through various inequalities.
    
    Args:
        graph: The graph to analyze
        
    Returns:
        int: Upper bound on genus
        
    Examples:
        >>> vertices = {"0", "1", "2", "3"}
        >>> edges = [("0", "1", 1), ("1", "2", 1), ("2", "3", 1), ("3", "0", 1)]
        >>> graph = CFGraph(vertices, edges)
        >>> genus_upper_bound(graph) >= 0
        True
    """
    n = len(graph.vertices)
    # Count total edges (considering multiple edges between vertices)
    m = sum(valence for v1 in graph.vertices 
            for v2, valence in graph.graph[v1].items() 
            if v1.name < v2.name)
    
    if n <= 2:
        return 0
    
    # Use Euler's formula: V - E + F = 2 - 2g
    # For a connected graph embedded in a surface of genus g
    # Rearranging: g = 1 - (V - E + F)/2
    # F ≥ 1 for connected graphs, so g ≤ 1 - (V - E + 1)/2 = (E - V + 1)/2
    
    return max(0, (m - n + 1) // 2)


def gonality_theoretical_bounds(graph: CFGraph) -> Dict[str, int]:
    """
    Compute various theoretical bounds for gonality.
    
    This includes bounds from independence number, treewidth, bramble order,
    and minimum degree as described in the octahedron theory.
    
    Args:
        graph: The graph to analyze
        
    Returns:
        Dict[str, int]: Dictionary of bound names to values
        
    Examples:
        >>> vertices = {"0", "1", "2", "3"}
        >>> edges = [("0", "1", 1), ("1", "2", 1), ("2", "3", 1), ("3", "0", 1)]
        >>> graph = CFGraph(vertices, edges)
        >>> bounds = gonality_theoretical_bounds(graph)
        >>> 'independence_upper_bound' in bounds
        True
    """
    n = len(graph.vertices)
    
    if n <= 1:
        return {'trivial_bound': 1}
    
    alpha = independence_number(graph)
    tw_bound = treewidth_upper_bound(graph)
    genus_bound = genus_upper_bound(graph)
    scramble_bound = scramble_number_upper_bound(graph)
    min_deg = minimum_degree(graph)
    bramble_bound = bramble_order_lower_bound(graph)
    
    bounds = {
        'trivial_lower_bound': 1,
        'trivial_upper_bound': n - 1,
        'independence_upper_bound': n - alpha,  # Theorem 1: gon(G) ≤ n - α(G)
        'treewidth_lower_bound': tw_bound,      # Theorem 2: tw(G) ≤ gon(G)
        'minimum_degree_bound': min_deg,        # δ(G) ≤ tw(G) ≤ gon(G)
        'bramble_order_bound': bramble_bound,   # Bramble order lower bound
        'genus_bound': genus_bound + 1,
        'scramble_bound': scramble_bound,
        'connectivity_bound': min(3, n - 1)
    }
    
    # Compute tighter bounds using the theoretical results
    lower_bound_candidates = [
        bounds['trivial_lower_bound'],
        bounds['minimum_degree_bound'],
        bounds['bramble_order_bound'] - 1,  # bramble order - 1 = treewidth lower bound
        max(1, bounds['connectivity_bound'] - 1)
    ]
    
    upper_bound_candidates = [
        bounds['trivial_upper_bound'],
        bounds['independence_upper_bound'],
        bounds['treewidth_lower_bound'] + 1,  # rough upper bound from treewidth
        bounds['scramble_bound']
    ]
    
    bounds['lower_bound'] = max(lower_bound_candidates)
    bounds['upper_bound'] = min(upper_bound_candidates)
    
    return bounds


def analyze_graph_properties(graph: CFGraph) -> Dict[str, any]:
    """
    Analyze various combinatorial properties relevant to gonality.
    
    Args:
        graph: The graph to analyze
        
    Returns:
        Dict[str, any]: Dictionary of properties and their values
        
    Examples:
        >>> vertices = {"0", "1", "2"}
        >>> edges = [("0", "1", 1), ("1", "2", 1)]
        >>> graph = CFGraph(vertices, edges)
        >>> props = analyze_graph_properties(graph)
        >>> 'num_vertices' in props
        True
    """
    n = len(graph.vertices)
    # Count total edges (considering multiple edges between vertices)
    m = sum(valence for v1 in graph.vertices 
            for v2, valence in graph.graph[v1].items() 
            if v1.name < v2.name)
    
    # Basic properties
    properties = {
        'num_vertices': n,
        'num_edges': m,
        'is_connected': is_connected(graph),
        'is_tree': m == n - 1 and is_connected(graph),
        'is_complete': m == n * (n - 1) // 2,
        'independence_number': independence_number(graph),
        'treewidth_upper_bound': treewidth_upper_bound(graph),
        'genus_upper_bound': genus_upper_bound(graph),
        'scramble_number_upper_bound': scramble_number_upper_bound(graph)
    }
    
    # Degree sequence
    degrees = []
    for vertex in graph.vertices:
        degree = graph.get_valence(vertex.name)
        degrees.append(degree)
    
    properties.update({
        'degree_sequence': sorted(degrees, reverse=True),
        'min_degree': min(degrees) if degrees else 0,
        'max_degree': max(degrees) if degrees else 0,
        'is_regular': len(set(degrees)) <= 1,
        'average_degree': sum(degrees) / len(degrees) if degrees else 0
    })
    
    # Gonality bounds
    properties['gonality_bounds'] = gonality_theoretical_bounds(graph)
    
    return properties

def graph_complement(graph: CFGraph) -> CFGraph:
    """
    Compute the complement of a graph.
    
    Args:
        graph: The input graph
        
    Returns:
        CFGraph: The complement graph
    """
    vertex_names = {vertex.name for vertex in graph.vertices}
    vertices = list(graph.vertices)
    edges = []
    
    # Add edges for all pairs not in original graph
    existing_edges = set()
    for v1 in graph.vertices:
        for v2 in graph.graph[v1]:
            existing_edges.add((min(v1.name, v2.name), max(v1.name, v2.name)))
    
    for i, v1 in enumerate(vertices):
        for j in range(i + 1, len(vertices)):
            v2 = vertices[j]
            edge_key = (min(v1.name, v2.name), max(v1.name, v2.name))
            if edge_key not in existing_edges:
                edges.append((v1.name, v2.name, 1))
    
    return CFGraph(vertex_names, edges)
