from .CFGraph import CFGraph
from .CFDivisor import CFDivisor
from .CFDhar import DharAlgorithm
from typing import Tuple, Optional

def EWD(graph: CFGraph, divisor: CFDivisor) -> Tuple[bool, Optional[CFDivisor]]:
    """
    Determine if a given chip-firing configuration is winnable using the Efficient Winnability Detection (EWD) algorithm.

    The EWD algorithm iteratively applies Dhar's algorithm to find and fire
    maximal legal firing sets until no more such sets can be found or the
    configuration becomes q-reduced with respect to a chosen vertex q.

    The vertex 'q' is chosen as the vertex with the minimum degree (most debt)
    in the initial configuration.

    Args:
        graph: The chip-firing graph (CFGraph instance).
        divisor: The initial chip distribution (CFDivisor instance).

    Returns:
        True if the configuration is winnable, False otherwise.

    Raises:
        ValueError: If the divisor has no degrees mapping, making it impossible
                    to determine the initial vertex 'q'.
    """

    # 1. Find the vertex 'q' with the minimum degree (most debt)
    if not divisor.degrees:
        raise ValueError("Cannot determine 'q': divisor has no degrees mapping.")

    # q is the Vertex object with the minimum degree.
    # min() is applied to (Vertex, degree) pairs from divisor.degrees.items().
    # - divisor.degrees.items() yields (Vertex, int) tuples.
    # - key=lambda item: item[1] tells min to compare items based on their second element (the degree).
    # - [0] extracts the Vertex object (the first element) from the (Vertex, degree) tuple
    #   that corresponds to the minimum degree.
    q = min(divisor.degrees.items(), key=lambda item: item[1])[0]

    # 2. Run Dhar's algorithm to find the maximal legal firing set
    dhar = DharAlgorithm(graph, divisor, q.name)
    # Initially run Dhar's to get the set of unburnt vertices (those not in the maximal legal firing set S_D(q)).
    unburnt_vertices = dhar.run()

    # 3. Iteratively fire maximal legal sets until q-reduced or no more sets can be fired.
    # The loop continues as long as Dhar's algorithm identifies a non-empty set of unburnt vertices.
    # This means there are still vertices that can be part of a legal firing sequence originating from q.
    while len(unburnt_vertices) > 0:
        unburnt_vertices = dhar.run()
        dhar.legal_set_fire(unburnt_vertices)

    # 4. If the degree of q is non-negative, then the graph is winnable
    deg_q = divisor.get_total_degree() - (
        dhar.configuration.get_total_degree() - dhar.configuration.get_degree(q.name)
    )
    dhar.configuration.degrees[q] = deg_q
    q_reduced_divisor = dhar.configuration

    if deg_q >= 0:
        return True, q_reduced_divisor 
    else:
        return False, q_reduced_divisor


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
    
    is_linearly_equivalent, _ = EWD(graph, difference_divisor)

    return is_linearly_equivalent

def is_winnable(divisor: CFDivisor) -> bool:
    """Check if a given chip-firing configuration is winnable.

    This function uses the Efficient Winnability Detection (EWD) algorithm to determine
    if the given chip-firing configuration is winnable.

    Args:
        divisor: The initial chip distribution (CFDivisor instance).

    Returns:
        True if the configuration is winnable, False otherwise.
    """
    is_winnable, _ = EWD(divisor.graph, divisor)
    return is_winnable

def q_reduction(divisor: CFDivisor) -> CFDivisor:
    """
    Perform a q-reduction on the given divisor.

    Args:
        divisor: The initial chip distribution (CFDivisor instance).

    Returns:
        The q-reduced divisor.
    """
    _, q_reduced_divisor = EWD(divisor.graph, divisor)
    return q_reduced_divisor

def is_q_reduced(divisor: CFDivisor) -> bool:
    """
    Check if the given divisor is q-reduced.

    Args:
        divisor: The initial chip distribution (CFDivisor instance).

    Returns:
        True if the divisor is q-reduced, False otherwise.
    """
    _, q_reduced_divisor = EWD(divisor.graph, divisor)
    return q_reduced_divisor == divisor

