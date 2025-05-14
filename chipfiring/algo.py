from .CFGraph import CFGraph, Vertex
from .CFDivisor import CFDivisor
from .CFDhar import DharAlgorithm
from .CFOrientation import CFOrientation
from typing import Tuple, Optional, List, Dict

import itertools
from multiprocessing import Pool

def EWD(graph: CFGraph, divisor: CFDivisor) -> Tuple[bool, Optional[CFDivisor], Optional[CFOrientation]]:
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
        A tuple containing:
        - Boolean indicating if the configuration is winnable
        - The q-reduced divisor (or None if not applicable)
        - The final orientation of edges tracking fire spread (or None if not applicable)

    Raises:
        ValueError: If the divisor has no degrees mapping, making it impossible
                    to determine the initial vertex 'q'.
        RuntimeError: If the final orientation is not full (some edges remain unoriented).
    """

    # 0. If total degree is negative, return False
    if divisor.get_total_degree() < 0:
        return False, None, None
    
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
    
    # Create a DharAlgorithm instance
    dhar = DharAlgorithm(graph, divisor, q.name)
    
    # Initially run Dhar's to get the set of unburnt vertices and orientation
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
        raise RuntimeError("The final orientation is not full. Some edges remain unoriented.")

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
    
    is_linearly_equivalent, _, _ = EWD(graph, difference_divisor)

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
    is_winnable, _, _ = EWD(divisor.graph, divisor)
    return is_winnable

def q_reduction(divisor: CFDivisor) -> CFDivisor:
    """
    Perform a q-reduction on the given divisor.

    Args:
        divisor: The initial chip distribution (CFDivisor instance).

    Returns:
        The q-reduced divisor.
    """
    _, q_reduced_divisor, _ = EWD(divisor.graph, divisor)
    return q_reduced_divisor

def is_q_reduced(divisor: CFDivisor) -> bool:
    """
    Check if the given divisor is q-reduced.

    Args:
        divisor: The initial chip distribution (CFDivisor instance).

    Returns:
        True if the divisor is q-reduced, False otherwise.
    """
    _, q_reduced_divisor, _ = EWD(divisor.graph, divisor)
    return q_reduced_divisor == divisor

def rank(divisor: CFDivisor) -> int:
    """
    Calculate the rank of a given divisor.

    The rank is computed as follows:
    1. If EWD(divisor) is not winnable, return -1.
    2. Starting with k = 1, consider all possible ways to remove k chips from
       the divisor such that the resulting divisor is effective (has non-negative chips).
    3. For each such resulting divisor, call EWD. These calls are done in parallel for a given k.
    4. If all EWD calls for the current k return winnable, increment k and repeat step 2.
    5. Otherwise (if any EWD call returns not winnable for the current k), return k - 1.
    6. If for a given k, no valid (effective) divisors can be formed by removing k chips (e.g., k is
       larger than the total number of chips in the original divisor), then all (zero) such ways are
       considered "winnable", and the rank is k-1. This effectively means the rank is the
       largest k' (equal to the current k-1) for which all removals were winnable.

    Args:
        divisor: The CFDivisor object for which to calculate the rank.

    Returns:
        The rank of the divisor. Returns -1 if the initial divisor is not winnable.
    """
    graph = divisor.graph

    # 1. Call EWD on the divisor; if unwinnable, return -1
    print("Step 1: Checking initial winnability...")
    initial_winnable, _, _ = EWD(graph, divisor)
    if not initial_winnable:
        print("Initial divisor is not winnable. Rank: -1")
        return -1
    print("Initial divisor is winnable.")

    sorted_vertices = sorted(list(graph.vertices), key=lambda v: v.name)

    k = 1
    print("Step 2: Iteratively removing k chips and checking winnability.")
    while True:
        print(f"\n-- Current k: {k} --")
        any_unwinnable_found_for_k = False
        processed_at_least_one_valid_divisor = False
        num_divisors_processed_for_k = 0

        # Nested generator for valid divisors for the current k
        def generate_valid_test_divisors_for_current_k():
            nonlocal processed_at_least_one_valid_divisor, num_divisors_processed_for_k # To modify the flag in the outer scope
            for chosen_vertices_to_decrement_combo in itertools.combinations_with_replacement(sorted_vertices, k):
                chips_to_remove_map: Dict[Vertex, int] = {v: 0 for v in sorted_vertices}
                for v_to_decrement in chosen_vertices_to_decrement_combo:
                    chips_to_remove_map[v_to_decrement] += 1

                new_degrees_list: List[Tuple[str, int]] = []
                for v_obj in sorted_vertices:
                    original_chips_at_v = divisor.get_degree(v_obj.name) # Uses the original divisor
                    num_chips_to_take = chips_to_remove_map[v_obj]
                    new_degrees_list.append((v_obj.name, original_chips_at_v - num_chips_to_take))
                
                subtracted_divisor = CFDivisor(graph, new_degrees_list)
                
                if subtracted_divisor.get_total_degree() >= 0:
                    processed_at_least_one_valid_divisor = True # A valid divisor is about to be yielded
                    yield subtracted_divisor
        
        try:
            print(f"  Starting parallel processing for k={k}...")
            # NOTE: Using Pool inside a loop like this creates and destroys pools repeatedly.
            # For many iterations of k, it might be more efficient to manage a single pool.
            with Pool() as pool:
                results_iterator = pool.imap_unordered(
                    is_winnable, # This function now needs to exist or be defined for the pool to call
                    generate_valid_test_divisors_for_current_k() # Call the generator
                )
                
                # Need to map results back to divisors if we want to print the divisor itself
                # For now, we just get winnability. To print divisor, _is_winnable_for_rank would need to return (divisor_str, winnable)
                # Or, re-generate/pass the divisors along with the winnability check call if printing is critical here.
                for winnable_result in results_iterator:
                    num_divisors_processed_for_k += 1
                    print(f"    Processed (k={k}, item {num_divisors_processed_for_k}): Winnable -> {winnable_result}")
                    if not winnable_result:
                        any_unwinnable_found_for_k = True
                        print(f"    Found unwinnable divisor for k={k}. Terminating pool for this k.")
                        pool.terminate() # Stop other tasks
                        pool.join()      # Wait for pool to clean up
                        break 
            print(f"  Parallel processing finished for k={k}.")
            
        except Exception as e:
            print(f"  Multiprocessing failed for k={k}: {e}. Falling back to sequential execution.")
            any_unwinnable_found_for_k = False # Reset for sequential run
            processed_at_least_one_valid_divisor = False # Reset for sequential run, generator will set it
            num_divisors_processed_for_k = 0 # Reset for sequential run
            
            print(f"  Starting sequential processing for k={k}...")
            for sub_divisor in generate_valid_test_divisors_for_current_k():
                num_divisors_processed_for_k += 1
                winnable_res, _, _ = EWD(sub_divisor.graph, sub_divisor)
                print(f"    Processed (k={k}, item {num_divisors_processed_for_k}): Divisor {sub_divisor.degrees_to_str()} -> Winnable: {winnable_res}")
                if not winnable_res:
                    any_unwinnable_found_for_k = True
                    print(f"    Found unwinnable divisor {sub_divisor.degrees_to_str()} for k={k}.")
                    break
            print(f"  Sequential processing finished for k={k}.")
        
        if not processed_at_least_one_valid_divisor:
            print(f"  For k={k}, no valid test divisors were generated (e.g., k too large). Rank: {k-1}")
            return k - 1  
        
        if any_unwinnable_found_for_k:
            print(f"  For k={k}, an unwinnable configuration was found. Rank: {k-1}")
            return k - 1
        else:
            print(f"  All {num_divisors_processed_for_k} processed configurations for k={k} were winnable. Incrementing k.")
            k += 1
            # Loop continues for the next k