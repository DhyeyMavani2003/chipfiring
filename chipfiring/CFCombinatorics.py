"""
Combinatorial tools for chip firing and gonality studies.

This module provides functions for parking functions, independent sets,
treewidth calculations, and scramble numbers as mentioned in the academic literature.
"""
from __future__ import annotations
import itertools
import warnings
from typing import Any, Dict, List, Optional, Set
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
        >>> is_parking_function([1, 3, 3])
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
    return graph.is_connected()


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
    
    For connected simple graphs, this provides a lower bound on treewidth and
    gonality: ``δ(G) ≤ tw(G) ≤ gon(G)``. With parallel edges, this function
    returns weighted valence and that inequality need not hold.
    
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
    
    This uses the relation between bramble order, treewidth, and gonality.
    
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
    if n == 0:
        return 0
    if not graph.is_connected():
        raise ValueError("Bramble bounds require a connected graph")

    # Degeneracy is at most treewidth, and the minimum degree of the whole
    # underlying simple graph is at most its degeneracy. Bramble order is
    # treewidth + 1. Parallel-edge multiplicities do not affect treewidth.
    simple_minimum_degree = min(len(graph.graph[vertex]) for vertex in graph.vertices)
    return simple_minimum_degree + 1


def complete_multipartite_gonality(partition_sizes: List[int]) -> int:
    """
    Compute the exact gonality of a complete multipartite graph K_{n1,n2,...,nk}.

    For at least two nonempty parts,
    ``gon(K_{n1,...,nk}) = n - max(ni)``.
    
    Args:
        partition_sizes: List of partition sizes
        
    Returns:
        int: The exact gonality
        
    Examples:
        >>> complete_multipartite_gonality([2, 2, 2])  # Octahedron K_{2,2,2}
        4
        >>> complete_multipartite_gonality([3, 4])  # K_{3,4}
        3
    """
    if len(partition_sizes) < 2:
        raise ValueError("At least two nonempty parts are required")
    if not all(type(size) is int and size > 0 for size in partition_sizes):
        raise ValueError("Partition sizes must be positive integers")

    return sum(partition_sizes) - max(partition_sizes)


def octahedron_independence_number() -> int:
    """
    Compute the independence number of the octahedron (K_{2,2,2}).
    
    As proven in the theory, the octahedron has independence number 2.
    
    Returns:
        int: The independence number (2)
    """
    return 2


def octahedron_bramble_construction() -> Dict[str, Any]:
    """
    Construct the bramble of order 5 on the octahedron as described in the theory.
    
    This bramble proves that the treewidth of the octahedron is at least 4.
    
    Returns:
        Dict[str, Any]: Information about the bramble construction
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
    Return the trivial vertex-count upper bound for scramble number.
    
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
    if n == 0:
        return 0
    if not graph.is_connected():
        raise ValueError("Scramble-number bounds require a connected graph")
    return n


def genus_upper_bound(graph: CFGraph) -> int:
    """
    Return the chip-firing genus (first Betti number) of a connected graph.

    The historical function name is retained for compatibility; the returned
    value is exact, not merely an upper bound.
    
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
    if not graph.vertices:
        return 0
    if not graph.is_connected():
        raise ValueError("Graph genus requires a connected graph")
    return graph.get_genus()


def gonality_theoretical_bounds(graph: CFGraph) -> Dict[str, int]:
    """
    Compute certified divisorial-gonality bounds for a connected simple graph.

    The lower bounds use vertex connectivity, minimum degree, and bramble
    order. The upper bounds use the vertex count, independence number, and the
    graph Riemann-Roch bound ``g + 1``. Multigraphs are rejected because the
    simple-graph independence and treewidth inequalities used here do not
    account for edge multiplicity.
    
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
    if n == 0:
        raise ValueError("Gonality bounds require a nonempty connected graph")
    if not graph.is_connected():
        raise ValueError("Gonality bounds require a connected graph")
    if any(valence != 1 for row in graph.graph.values() for valence in row.values()):
        raise ValueError("These gonality bounds require a simple graph")

    if n == 1:
        return {
            'trivial_bound': 1,
            'trivial_lower_bound': 1,
            'trivial_upper_bound': 1,
            'independence_upper_bound': 1,
            'treewidth_lower_bound': 0,
            'treewidth_upper_estimate': 0,
            'minimum_degree_bound': 0,
            'bramble_order_bound': 1,
            'genus_bound': 1,
            'connectivity_bound': 0,
            'lower_bound': 1,
            'upper_bound': 1,
        }

    nx_graph = nx.Graph()
    nx_graph.add_nodes_from(vertex.name for vertex in graph.vertices)
    nx_graph.add_edges_from(
        (vertex.name, neighbor.name)
        for vertex in graph.vertices
        for neighbor in graph.graph[vertex]
        if vertex.name < neighbor.name
    )

    alpha = independence_number(graph)
    min_deg = minimum_degree(graph)
    connectivity = nx.node_connectivity(nx_graph)
    bramble_bound = bramble_order_lower_bound(graph)
    certified_treewidth_lower = max(min_deg, connectivity, bramble_bound - 1)

    bounds = {
        'trivial_lower_bound': 1,
        'trivial_upper_bound': n,
        'independence_upper_bound': n - alpha,
        'treewidth_lower_bound': certified_treewidth_lower,
        'treewidth_upper_estimate': treewidth_upper_bound(graph),
        'minimum_degree_bound': min_deg,
        'bramble_order_bound': bramble_bound,
        'genus_bound': graph.get_genus() + 1,
        'scramble_bound': scramble_number_upper_bound(graph),
        'connectivity_bound': connectivity,
    }
    bounds['lower_bound'] = max(
        bounds['trivial_lower_bound'],
        bounds['treewidth_lower_bound'],
    )
    bounds['upper_bound'] = min(
        bounds['trivial_upper_bound'],
        bounds['independence_upper_bound'],
        bounds['genus_bound'],
    )
    return bounds


def analyze_graph_properties(graph: CFGraph) -> Dict[str, Any]:
    """
    Analyze various combinatorial properties relevant to gonality.
    
    Args:
        graph: The graph to analyze
        
    Returns:
        Dict[str, Any]: Dictionary of properties and their values
        
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
    
    connected = is_connected(graph)
    graph_genus = genus_upper_bound(graph) if connected else None
    scramble_upper = scramble_number_upper_bound(graph) if connected else None

    # Basic properties
    properties = {
        'num_vertices': n,
        'num_edges': m,
        'is_connected': connected,
        'is_tree': m == n - 1 and connected,
        'is_complete': m == n * (n - 1) // 2,
        'independence_number': independence_number(graph),
        'treewidth_upper_bound': treewidth_upper_bound(graph),
        'genus_upper_bound': graph_genus,
        'scramble_number_upper_bound': scramble_upper,
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
    
    try:
        properties['gonality_bounds'] = gonality_theoretical_bounds(graph)
        properties['gonality_bounds_unavailable_reason'] = None
    except ValueError as error:
        properties['gonality_bounds'] = None
        properties['gonality_bounds_unavailable_reason'] = str(error)
    
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

def icosahedron_independence_number() -> int:
    """
    Compute the independence number of the icosahedron.
    
    The icosahedron has independence number α(I) = 3.
    
    Returns:
        int: The independence number (3)
    """
    return 3


def icosahedron_2_uniform_scramble() -> Dict[str, Any]:
    """
    Return the all-edges 2-uniform scramble on the icosahedron.

    Beougher et al., "Chip-firing on the Platonic solids: a primer for studying
    graph gonality," use all 30 edges as the connected two-vertex eggs. Its
    hitting number is 9 and its egg-cut number is 8, so its norm is 8.
    
    Returns:
        Dict containing scramble construction details
    """
    nx_graph = nx.icosahedral_graph()
    scramble_sets = [
        {f"v{source}", f"v{target}"}
        for source, target in sorted(nx_graph.edges())
    ]
    hitting_number = 12 - icosahedron_independence_number()
    egg_cut_number = icosahedron_egg_cut_number()['egg_cut_number']

    return {
        'scramble_sets': scramble_sets,
        'hitting_number': hitting_number,
        'egg_cut_number': egg_cut_number,
        'scramble_norm': min(hitting_number, egg_cut_number),
        'is_2_uniform': True,
        'description': 'All-edge 2-uniform scramble on the icosahedron',
        'vertex_pairs': len(scramble_sets),
        'construction_type': 'all_edges'
    }


def icosahedron_screewidth_bound() -> Dict[str, int]:
    """
    Return the known scramble-number and screewidth values for the icosahedron.

    The all-edge scramble gives ``sn(I) >= 8``. A width-8 tree-cut
    decomposition gives ``scw(I) <= 8``, and ``sn(I) <= scw(I)``, so both
    parameters equal 8.
    
    Returns:
        Dict containing screewidth bounds
    """
    return {
        'screewidth_upper_bound': 8,
        'screewidth': 8,
        'scramble_number_bound': 8,
        'scramble_number': 8,
        'relation': '||S|| = 8 ≤ sn(I) ≤ scw(I) ≤ 8',
        'tree_cut_decomposition_bags': [
            ('v0', 'v1'),
            ('v2', 'v5', 'v6', 'v7', 'v8', 'v9', 'v10', 'v11'),
            ('v3', 'v4'),
        ],
        'tree_cut_edge_widths': [8, 8],
        'tree_cut_decomposition_bag_sizes': [2, 8, 2],
        'tightness': 'matching_scramble_and_tree_cut_bounds'
    }


def icosahedron_subgraph_outdegree_bounds() -> Dict[str, Any]:
    """
    Compute edge-boundary minima for vertex subsets of the icosahedron.

    The reference lower bounds are 8 for subset orders 2 and 10, and 9
    for orders 3 through 9. This function exhaustively computes the actual
    minimum cut size for every nontrivial subset order and verifies those
    bounds directly.

    Returns:
        Dictionary containing actual and reference lower bounds by subset size.
    """
    graph = nx.icosahedral_graph()
    vertices = tuple(sorted(graph.nodes()))
    actual_minimum_by_order = {}
    for order in range(1, len(vertices)):
        actual_minimum_by_order[order] = min(
            nx.cut_size(graph, subset, set(vertices) - set(subset))
            for subset in itertools.combinations(vertices, order)
        )

    reference_lower_bound_by_order = {
        order: 8 if order in {2, 10} else 9
        for order in range(2, 11)
    }
    return {
        'actual_minimum_outdegree_by_order': actual_minimum_by_order,
        'reference_lower_bound_by_order': reference_lower_bound_by_order,
        'minimum_reference_bound': min(reference_lower_bound_by_order.values()),
        'reference_bounds_verified': all(
            actual_minimum_by_order[order] >= lower_bound
            for order, lower_bound in reference_lower_bound_by_order.items()
        ),
        'source': (
            'Beougher et al., "Chip-firing on the Platonic solids: '
            'a primer for studying graph gonality"'
        ),
    }


def icosahedron_gonality_proof_summary() -> Dict[str, Any]:
    """
    Return a literature-backed summary of the gonality-9 result.

    This function does not execute an exhaustive Dhar calculation. It records
    the published upper- and lower-bound statements so callers can distinguish
    reference data from values computed by this package.

    Returns:
        Dictionary containing the exact published value and proof methods.
    """
    return {
        'published_exact_value': 9,
        'upper_bound': 9,
        'upper_bound_method': 'independence-number divisor construction',
        'lower_bound': 9,
        'lower_bound_method': 'Dhar burning and subgraph outdegree analysis',
        'lower_bound_statement': (
            'No effective divisor of degree 8 on the icosahedron has rank at least 1'
        ),
        'computed_by_package': False,
        'source': (
            'Beougher et al., "Chip-firing on the Platonic solids: '
            'a primer for studying graph gonality"'
        ),
    }


def icosahedron_lemma_3_subgraph_bounds() -> Dict[str, Any]:
    """Deprecated compatibility wrapper for subgraph outdegree data."""
    warnings.warn(
        "Use icosahedron_subgraph_outdegree_bounds instead",
        DeprecationWarning,
        stacklevel=2,
    )
    data = icosahedron_subgraph_outdegree_bounds()
    return {
        **data,
        'max_outdegree_bound': data['minimum_reference_bound'],
        'independence_number': 3,
        'critical_subgraphs': [
            {
                'name': 'order_2_subgraphs',
                'vertices': 2,
                'max_outdegree': 8,
                'minimum_outdegree': 8,
                'contributes_to_gonality': True,
            },
            {
                'name': 'orders_3_through_9',
                'vertices': 3,
                'orders': tuple(range(3, 10)),
                'max_outdegree': 9,
                'minimum_outdegree': 9,
                'contributes_to_gonality': True,
            },
            {
                'name': 'order_10_subgraphs',
                'vertices': 10,
                'max_outdegree': 8,
                'minimum_outdegree': 8,
                'contributes_to_gonality': True,
            },
        ],
        'lemma_statement': 'Subgraph outdegree bounds for effective divisors',
        'contributes_to_gonality_proof': True,
    }


def icosahedron_dhars_burning_algorithm() -> Dict[str, Any]:
    """Deprecated compatibility wrapper for the published proof summary."""
    warnings.warn(
        "Use icosahedron_gonality_proof_summary instead",
        DeprecationWarning,
        stacklevel=2,
    )
    summary = icosahedron_gonality_proof_summary()
    return {
        **summary,
        'gonality': summary['published_exact_value'],
        'debt_free_divisor_exists': {
            'degree': 9,
            'exists': True,
            'construction': 'published_rank_one_divisor',
            'proof_method': 'independence-number upper bound',
            'description': 'A published degree-9 divisor of rank at least 1 exists',
        },
        'no_lower_degree_divisor': {
            'degree': 8,
            'exists': False,
            'reason': 'published_Dhar_and_subgraph_outdegree_analysis',
            'description': 'No effective degree-8 divisor has rank at least 1',
        },
        'burning_sequences': [
            {
                'initial_debt': 8,
                'burning_rounds': 0,
                'debt_propagation': 'reference_proof_excludes_rank_one',
                'conclusion': 'degree_8_rank_one_impossible',
                'computed_by_package': False,
            },
            {
                'initial_debt': 9,
                'burning_rounds': 0,
                'debt_propagation': 'reference_construction_establishes_rank_one',
                'conclusion': 'degree_9_rank_one_exists',
                'computed_by_package': False,
            },
        ],
        'algorithm': 'published_Dhar_analysis',
        'theorem_reference': summary['source'],
        'proof_complete': True,
    }


def icosahedron_egg_cut_number() -> Dict[str, Any]:
    """
    Compute the egg-cut number for the icosahedron.
    
    The egg-cut number is related to scramble theory and provides
    another perspective on gonality bounds.
    
    Returns:
        Dict containing egg-cut number analysis
    """
    graph = nx.icosahedral_graph()
    vertices = set(graph.nodes())
    best_cut_size = None
    best_subset = None
    best_cut_edges = None
    for order in range(2, len(vertices) // 2 + 1):
        for subset_tuple in itertools.combinations(sorted(vertices), order):
            subset = set(subset_tuple)
            complement = vertices - subset
            if graph.subgraph(subset).number_of_edges() == 0:
                continue
            if graph.subgraph(complement).number_of_edges() == 0:
                continue
            cut_edges = sorted(
                (source, target)
                for source, target in graph.edges()
                if (source in subset) != (target in subset)
            )
            if best_cut_size is None or len(cut_edges) < best_cut_size:
                best_cut_size = len(cut_edges)
                best_subset = subset
                best_cut_edges = cut_edges

    if best_cut_size is None or best_subset is None or best_cut_edges is None:
        raise RuntimeError("Failed to find a valid egg-separating cut")

    return {
        'egg_cut_number': best_cut_size,
        'lower_bound': best_cut_size,
        'upper_bound': best_cut_size,
        'witness_side': {f"v{vertex}" for vertex in best_subset},
        'witness_cut_edges': [
            (f"v{source}", f"v{target}") for source, target in best_cut_edges
        ],
        'relation_to_scramble': 'egg-cut number of the all-edge 2-uniform scramble',
        'contributes_to_gonality': True,
    }


def icosahedron_hitting_set_analysis() -> Dict[str, Any]:
    """
    Analyze hitting sets for the icosahedron scramble construction.
    
    This implements the hitting set computations that appear in
    the scramble number analysis.
    
    Returns:
        Dict containing hitting set analysis
    """
    scramble_info = icosahedron_2_uniform_scramble()
    scramble_sets = scramble_info['scramble_sets']
    graph = nx.icosahedral_graph()
    complement = nx.complement(graph)
    independent_sets = sorted(
        (
            tuple(sorted(clique))
            for clique in nx.find_cliques(complement)
            if len(clique) == icosahedron_independence_number()
        )
    )
    all_vertices = set(graph.nodes())
    hitting_sets = [
        {f"v{vertex}" for vertex in all_vertices - set(independent_set)}
        for independent_set in independent_sets
    ]
    min_hitting_set_size = 12 - icosahedron_independence_number()

    hitting_set_bounds = {
        'minimum_size': min_hitting_set_size,
        'maximum_size': 12,  # All vertices
        'optimal_size': min_hitting_set_size,
        'relation_to_scramble': 'minimum vertex cover of the icosahedron'
    }
    
    return {
        'scramble_sets': scramble_sets,
        'hitting_sets': hitting_sets,
        'hitting_set_bounds': hitting_set_bounds,
        'minimum_hitting_set_size': min_hitting_set_size,
        'analysis_type': 'scramble_hitting_set_computation'
    }


def icosahedron_gonality_theoretical_bounds() -> Dict[str, Any]:
    """
    Return literature-backed invariants and exact gonality of the icosahedron.
    
    Returns:
        Dict containing all theoretical bounds
    """
    n_vertices = 12
    independence_upper_bound = n_vertices - icosahedron_independence_number()
    scramble_info = icosahedron_2_uniform_scramble()
    screewidth_info = icosahedron_screewidth_bound()
    subgraph_info = icosahedron_subgraph_outdegree_bounds()
    proof_summary = icosahedron_gonality_proof_summary()

    return {
        'trivial_lower_bound': 1,
        'trivial_upper_bound': n_vertices - 1,
        'vertex_count_upper_bound': n_vertices,
        'independence_upper_bound': independence_upper_bound,
        'scramble_number_bound': scramble_info['scramble_norm'],
        'screewidth_bound': screewidth_info['screewidth'],
        'subgraph_outdegree_lower_bound': subgraph_info['minimum_reference_bound'],
        'subgraph_outdegree_bound': subgraph_info['minimum_reference_bound'],
        'degree_based_bound': 5,
        'dhars_algorithm_result': proof_summary['published_exact_value'],
        'exact_gonality': proof_summary['published_exact_value'],
        'published_exact_value': proof_summary['published_exact_value'],
        'lower_bound': proof_summary['lower_bound'],
        'upper_bound': proof_summary['upper_bound'],
        'source': proof_summary['source'],
    }
