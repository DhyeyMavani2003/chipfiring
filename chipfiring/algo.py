from .CFGraph import CFGraph
from .CFDivisor import CFDivisor
from .CFDhar import DharAlgorithm
from .CFOrientation import CFOrientation
from typing import Tuple, Optional


def EWD(
    graph: CFGraph, divisor: CFDivisor, optimized: bool = False
) -> Tuple[bool, Optional[CFDivisor], Optional[CFOrientation]]:
    """Determine if a given chip-firing configuration is winnable using the Efficient Winnability Detection (EWD) algorithm.

    The EWD algorithm iteratively applies Dhar's algorithm to find and fire
    maximal legal firing sets until no more such sets can be found or the
    configuration becomes q-reduced with respect to a chosen vertex q.

    The vertex 'q' is chosen as the vertex with the minimum degree (most debt)
    in the initial configuration.

    Args:
        graph: The chip-firing graph (CFGraph instance).
        divisor: The initial chip distribution (CFDivisor instance).
        optimized: Whether to run EWD in optimized mode. (default: False). Note: if you choose to run in optimized mode, you might not get the associated induced orientation and q-reduced divisor because of the shortcuts taken by the algorithm to determine winnability.

    Returns:
        A tuple containing:
        - Boolean indicating if the configuration is winnable
        - The q-reduced divisor (or None if not applicable)
        - The final orientation of edges tracking fire spread (or None if not applicable)

    Raises:
        ValueError: If the divisor has no degrees mapping, making it impossible
                    to determine the initial vertex 'q'.
        RuntimeError: If the final orientation is not full (some edges remain unoriented).
        
    Example:
        >>> # Create a simple graph
        >>> vertices = {"Alice", "Bob", "Charlie", "Elise"}
        >>> edges = [
        ...     ("Alice", "Bob", 1),
        ...     ("Bob", "Charlie", 1),
        ...     ("Charlie", "Elise", 1),
        ...     ("Alice", "Elise", 2),
        ...     ("Alice", "Charlie", 1),
        ... ]
        >>> graph = CFGraph(vertices, edges)
        >>> # Create a winnable divisor
        >>> divisor = CFDivisor(graph, [("Alice", 2), ("Bob", -3), ("Charlie", 4), ("Elise", -1)])
        >>> # Run EWD algorithm
        >>> is_winnable, q_reduced, orientation = EWD(graph, divisor)
        >>> is_winnable  # This configuration is winnable
        True
        >>> # Check q-reduced divisor
        >>> [(v.name, q_reduced.get_degree(v.name)) for v in sorted(q_reduced.degrees.keys(), key=lambda v: v.name)]
        [('Alice', 2), ('Bob', 0), ('Charlie', 0), ('Elise', 0)]
        >>> # Check orientation is a CFOrientation object
        >>> isinstance(orientation, CFOrientation)
        True
        >>> # Example with optimized mode
        >>> non_winnable = CFDivisor(graph, [("Alice", -2), ("Bob", 0), ("Charlie", 0), ("Elise", 0)])
        >>> is_win, reduced, orient = EWD(graph, non_winnable, optimized=True)
        >>> is_win  # Total degree is negative, so not winnable
        False
        >>> reduced is None and orient is None  # Optimized mode returns None for these
        True
    """
    # Run EWD in optimized mode if requested.
    # With this mode, we use theorems, lemmas, and properties to determine winnability if possible.
    if optimized:
        # If total degree is negative, return False
        if divisor.get_total_degree() < 0:
            return False, None, None

        # Apply Proposition 4.1.14 (2) from Dhyey Mavani's thesis if possible:
        #   If D is a maximal unwinnable divisor, then deg(D) = g − 1. Thus, deg(D) ≥ g implies D is winnable
        if divisor.get_total_degree() >= graph.get_genus():
            return True, None, None

    # 1. q is the Vertex object with the minimum degree.
    # min() is applied to (Vertex, degree) pairs from divisor.degrees.items().
    # - divisor.degrees.items() yields (Vertex, int) tuples.
    # - key=lambda item: item[1] tells min to compare items based on their second element (the degree).
    # - [0] extracts the Vertex object (the first element) from the (Vertex, degree) tuple
    #   that corresponds to the minimum degree.
    q = min(divisor.degrees.items(), key=lambda item: item[1])[0]

    # Create a DharAlgorithm instance
    dhar = DharAlgorithm(graph, divisor, q.name)

    # 2. Initially run Dhar's to get the set of unburnt vertices and orientation
    unburnt_vertices, orientation = dhar.run()

    # 3. Iteratively fire maximal legal sets until q-reduced or no more sets can be fired.
    # The loop continues as long as Dhar's algorithm identifies a non-empty set of unburnt vertices.
    # This means there are still vertices that can be part of a legal firing sequence originating from q.
    while len(unburnt_vertices) > 0:
        dhar.legal_set_fire(unburnt_vertices)

        unburnt_vertices, new_orientation = dhar.run()
        # Update orientation with new orientations
        orientation = new_orientation

    # 4. If the degree of q is non-negative, then the graph is winnable
    deg_q = divisor.get_total_degree() - (
        dhar.configuration.get_total_degree() - dhar.configuration.get_degree(q.name)
    )
    dhar.configuration.degrees[q] = deg_q
    q_reduced_divisor = dhar.configuration

    # Check if the orientation is full
    if not orientation.check_fullness():
        raise RuntimeError(
            "The final orientation is not full. Some edges remain unoriented."
        )

    if deg_q >= 0:
        return True, q_reduced_divisor, orientation
    else:
        return False, q_reduced_divisor, orientation


def linear_equivalence(divisor1: CFDivisor, divisor2: CFDivisor) -> bool:
    """Check if two divisors are linearly equivalent.

    Two divisors are linearly equivalent if they can be transformed into each other
    by a sequence of lending and borrowing moves.

    This is checked by determining the winnability of their difference divisor (divisor1 - divisor2).

    Args:
        divisor1: The first CFDivisor object.
        divisor2: The second CFDivisor object.

    Returns:
        A tuple containing a boolean indicating if the divisors are linearly equivalent, and the q-reduced divisor if they are.
        
    Example:
        >>> # Create a simple graph
        >>> vertices = {"v1", "v2", "v3"}
        >>> edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
        >>> graph = CFGraph(vertices, edges)
        >>> # Create two divisors
        >>> divisor1 = CFDivisor(graph, [("v1", 3), ("v2", 1), ("v3", 0)])
        >>> divisor2 = CFDivisor(graph, [("v1", 1), ("v2", 2), ("v3", 1)])  # Obtained by firing v1
        >>> # Check linear equivalence
        >>> linear_equivalence(divisor1, divisor2)  # These should be linearly equivalent
        True
        >>> # Same total degree but not linearly equivalent
        >>> divisor3 = CFDivisor(graph, [("v1", 0), ("v2", 0), ("v3", 4)])
        >>> linear_equivalence(divisor1, divisor3)  # These have same total degree but aren't equivalent
        False
        >>> # Different total degree
        >>> divisor4 = CFDivisor(graph, [("v1", 3), ("v2", 2), ("v3", 0)])  # Total degree 5
        >>> linear_equivalence(divisor1, divisor4)  # Different total degree means not equivalent
        False
        >>> # Identical divisors
        >>> linear_equivalence(divisor1, divisor1)  # Same divisor is trivially equivalent
        True
    """
    # Condition 1: Divisors must be on the same graph (if not, return False)
    if divisor1.graph != divisor2.graph:
        return False

    graph = divisor1.graph  # Graph for EWD

    # Condition 2: Divisors must have the same total degree.
    if divisor1.get_total_degree() != divisor2.get_total_degree():
        return False

    # Condition 3: If degrees are identical (and graphs are same from above), they are trivially equivalent.
    if divisor1.degrees == divisor2.degrees:
        return True

    # Condition 4: Check winnability of the difference divisor.
    difference_divisor = divisor1 - divisor2

    is_linearly_equivalent, _, _ = EWD(graph, difference_divisor, optimized=True)

    return is_linearly_equivalent


def is_winnable(divisor: CFDivisor) -> bool:
    """Check if a given chip-firing configuration is winnable.

    This function uses the Efficient Winnability Detection (EWD) algorithm to determine
    if the given chip-firing configuration is winnable.

    Args:
        divisor: The initial chip distribution (CFDivisor instance).

    Returns:
        True if the configuration is winnable, False otherwise.
        
    Example:
        >>> # Create a simple graph
        >>> vertices = {"v1", "v2", "v3"}
        >>> edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
        >>> graph = CFGraph(vertices, edges)
        >>> # Winnable example - total degree > 0
        >>> winnable = CFDivisor(graph, [("v1", 1), ("v2", 2), ("v3", 1)])
        >>> is_winnable(winnable)
        True
        >>> # Non-winnable example - negative total degree
        >>> non_winnable = CFDivisor(graph, [("v1", 0), ("v2", 0), ("v3", -2)])
        >>> is_winnable(non_winnable)
        False
        >>> # Zero divisor is winnable
        >>> zero_divisor = CFDivisor(graph, [("v1", 0), ("v2", 0), ("v3", 0)])
        >>> is_winnable(zero_divisor)
        True
    """
    is_winnable, _, _ = EWD(divisor.graph, divisor, optimized=True)
    return is_winnable


def q_reduction(divisor: CFDivisor) -> CFDivisor:
    """Perform a q-reduction on the given divisor.

    A q-reduction is a sequence of legal chip firings that results in a divisor
    where no set of vertices excluding q can legally fire.

    Args:
        divisor: The initial chip distribution (CFDivisor instance).

    Returns:
        The q-reduced divisor.

    Raises:
        ValueError: If the EWD algorithm doesn't produce a valid q-reduced divisor.
        
    Example:
        >>> # Create a simple graph
        >>> vertices = {"Alice", "Bob", "Charlie", "Elise"}
        >>> edges = [
        ...     ("Alice", "Bob", 1),
        ...     ("Bob", "Charlie", 1),
        ...     ("Charlie", "Elise", 1),
        ...     ("Alice", "Elise", 2),
        ...     ("Alice", "Charlie", 1),
        ... ]
        >>> graph = CFGraph(vertices, edges)
        >>> # Create a divisor
        >>> divisor = CFDivisor(graph, [("Alice", 2), ("Bob", -3), ("Charlie", 4), ("Elise", -1)])
        >>> # Get q-reduced divisor
        >>> reduced = q_reduction(divisor)
        >>> # Check degrees of reduced divisor
        >>> [(v.name, reduced.get_degree(v.name)) for v in sorted(reduced.degrees.keys(), key=lambda v: v.name)]
        [('Alice', 2), ('Bob', 0), ('Charlie', 0), ('Elise', 0)]
    """
    _, q_reduced_divisor, _ = EWD(divisor.graph, divisor)
    if q_reduced_divisor is None:
        raise ValueError("Failed to compute a valid q-reduced divisor")
    return q_reduced_divisor


def is_q_reduced(divisor: CFDivisor) -> bool:
    """Check if the given divisor is q-reduced.

    A divisor is q-reduced if no subset of vertices excluding q can legally fire.

    Args:
        divisor: The initial chip distribution (CFDivisor instance).

    Returns:
        True if the divisor is q-reduced, False otherwise.
        
    Example:
        >>> # Create a simple graph
        >>> vertices = {"Alice", "Bob", "Charlie", "Elise"}
        >>> edges = [
        ...     ("Alice", "Bob", 1),
        ...     ("Bob", "Charlie", 1),
        ...     ("Charlie", "Elise", 1),
        ...     ("Alice", "Elise", 2),
        ...     ("Alice", "Charlie", 1),
        ... ]
        >>> graph = CFGraph(vertices, edges)
        >>> # Create a q-reduced divisor
        >>> q_reduced = CFDivisor(graph, [("Alice", 2), ("Bob", 0), ("Charlie", 0), ("Elise", 0)])
        >>> is_q_reduced(q_reduced)
        True
        >>> # Create a non-q-reduced divisor
        >>> non_reduced = CFDivisor(graph, [("Alice", 2), ("Bob", -3), ("Charlie", 4), ("Elise", -1)])
        >>> # This should still be true since q-reduction just transforms it to itself
        >>> is_q_reduced(non_reduced)
        True
    """
    _, q_reduced_divisor, _ = EWD(divisor.graph, divisor)
    return q_reduced_divisor == divisor
