"""
Rank calculation for divisors on chip-firing graphs.

This module provides functionality to calculate the rank of divisors on chip-firing graphs,
which is an important invariant in the theory of divisors on graphs. The rank measures
how much freedom you have to move chips around while keeping the divisor effective.

The implementation uses the Efficient Winnability Detection (EWD) algorithm as a building
block and provides both standard and optimized calculation modes.
"""
from __future__ import annotations
from .CFDivisor import CFDivisor
from .CFOrientation import CFOrientation
from .algo import EWD
import itertools
from multiprocessing import Pool, cpu_count
from collections import Counter


class CFRank:
    """
    A class that holds the result of a rank calculation.

    This class stores both the computed rank value of a divisor and the detailed
    logs of the calculation process. It is typically created and returned by the
    `rank()` function rather than being instantiated directly.

    Attributes:
        logs (List[str]): Sequential log messages from the rank calculation process.
        rank (int): The computed rank value, accessible as a property.

    Example:
        >>> result = rank(divisor)
        >>> print(f"The rank is: {result.rank}")
        >>> for log in result.logs:
        ...     print(log)
    """

    def __init__(self):
        """Internal constructor to initialize the CFRank object."""
        self.logs = []
        self._rank_value = None
        self._divisor = None

    def log(self, message: str):
        """Internal method to add a log message to the logs list."""
        self.logs.append(message)

    @property
    def rank(self) -> int:
        """
        Retrieve the calculated rank value.

        Returns:
            int: The rank value of the divisor.

        Raises:
            ValueError: If no rank calculation has been performed yet.
        """
        if self._rank_value is None:
            raise ValueError("No rank has been calculated yet.")
        return self._rank_value

    def _calculate_rank(self, divisor: CFDivisor, optimized: bool = False) -> "CFRank":
        """
        Internal method to calculate the rank of a given divisor.
        """
        self.logs = []  # Reset logs for new calculation
        self._divisor = divisor
        graph = divisor.graph

        if optimized:
            # Heuristic shortcut from Backman, Riemann-Roch theory for graph
            # orientations (arXiv:1401.3309): a divisor of negative total
            # degree cannot be linearly equivalent to an effective divisor,
            # so its rank is -1 without invoking EWD.
            if divisor.get_total_degree() < 0:
                self.log(
                    "Optimized mode: total degree of D is negative, so D is not "
                    "equivalent to any effective divisor. Skipping EWD; rank: -1."
                )
                self._rank_value = -1
                return self

        # 1. Call EWD on the divisor; if unwinnable, return -1
        self.log("Step 1: Checking initial winnability through EWD algorithm...")
        initial_winnable, _, _, _ = EWD(graph, divisor, optimized=False)
        if not initial_winnable:
            self.log("Initial divisor is not winnable. So, rank: -1")
            self._rank_value = -1
            return self
        self.log("Initial divisor is winnable. Proceeding to step 2.")

        # Lower bound k0 from which we may safely start the search. By
        # convention the search begins at k=1.
        k_start = 1

        if optimized:
            self.log(
                "Optimized mode is enabled. Checking if we can apply theoretical shortcuts before proceeding."
            )

            D = self._divisor
            g = graph.get_genus()

            # Using Corollary 4.4.3 from Dhyey Mavani's Math thesis:
            if D.get_total_degree() > 2 * g - 2:
                self.log(
                    "Optimized mode: D has degree > 2g-2. Using Corollary 4.4.3 from Dhyey Mavani's Math thesis to skip step 2, and return rank(D) = degree(D) - genus(G)."
                )
                self._rank_value = D.get_total_degree() - g
                return self

            # Riemann-Roch lower bound (Backman, arXiv:1401.3309, building on
            # the Baker-Norine Riemann-Roch theorem for graphs):
            #   r(D) >= deg(D) - g
            # When deg(D) >= g + 1 this gives a strictly positive lower bound
            # on r(D), so the search can skip all k <= deg(D) - g: for any
            # effective E with deg(E) <= deg(D) - g the divisor D - E is
            # automatically winnable. We apply this directly to D (rather
            # than to K-D) so that the loop computes r(D).
            deg_D = D.get_total_degree()
            rr_lower = deg_D - g
            if rr_lower >= 1:
                k_start = rr_lower + 1
                self.log(
                    f"Optimized mode: Riemann-Roch gives r(D) >= deg(D) - g = "
                    f"{deg_D} - {g} = {rr_lower}. Starting search at k={k_start} "
                    f"instead of k=1."
                )
            else:
                # No useful Riemann-Roch lower bound; fall back to the
                # existing K-D heuristic which can shrink the search space
                # when deg(K-D) < deg(D).
                orientation = CFOrientation(graph, [])
                K = orientation.canonical_divisor()
                if (K - D).get_total_degree() < D.get_total_degree():
                    self.log(
                        "Optimized mode: (K-D) has lower degree than D. Running next step on (K-D)."
                    )
                    self._divisor = K - D
                else:
                    self.log(
                        "Optimized mode: (K-D) has degree >= that of D. Running next step on D itself."
                    )

        # 2. Sort the vertices by name
        sorted_vertices = sorted(list(graph.vertices), key=lambda v: v.name)

        k = k_start
        self.log("Step 2: Iteratively removing k chips and checking winnability.")
        while True:
            self.log(f"\n-- Current k: {k} --")

            def generate_sub_divisors_for_k():
                """
                Generates all divisors D-E where E is an effective divisor of degree k.
                """
                # Create all effective divisors E of degree k.
                # An effective divisor is a sum of vertices, so we can get all of them
                # by taking combinations with replacement of the vertices.
                for combination_of_vertices in itertools.combinations_with_replacement(
                    sorted_vertices, k
                ):
                    vertex_counts = Counter(v.name for v in combination_of_vertices)

                    # Create the divisor E to subtract
                    subtraction_divisor = CFDivisor(
                        graph, list(vertex_counts.items())
                    )

                    # Return D - E
                    yield self._divisor - subtraction_divisor

            any_unwinnable_found_for_k = False
            num_divisors_processed_for_k = 0

            def _check_winnability(sub_divisor):
                nonlocal num_divisors_processed_for_k
                num_divisors_processed_for_k += 1
                winnable, _, _, _ = EWD(
                    sub_divisor.graph, sub_divisor, optimized=False
                )
                if not winnable:
                    # Log from the worker process if an unwinnable divisor is found
                    # This might not be perfectly sequential in the main log, but it's informative
                    print(
                        f"    Found unwinnable divisor for k={k}. Terminating pool for this k."
                    )
                return winnable

            try:
                self.log(f"  Starting parallel processing for k={k}...")
                with Pool(processes=cpu_count()) as pool:
                    # The number of divisors can be large, so use imap_unordered for lazy evaluation
                    results_iterator = pool.imap_unordered(
                        _check_winnability,
                        generate_sub_divisors_for_k(),
                    )

                    for i, winnable_res in enumerate(results_iterator):
                        self.log(f"    Processed (k={k}, item {i+1}): Winnable -> {winnable_res}")
                        if not winnable_res:
                            any_unwinnable_found_for_k = True
                            pool.terminate()  # Stop processing further items for this k
                            break

                self.log(f"  Parallel processing finished for k={k}.")

            except Exception as e:
                self.log(
                    f"  Multiprocessing failed for k={k}: {e}. Falling back to sequential execution."
                )
                any_unwinnable_found_for_k = False  # Reset for sequential run
                num_divisors_processed_for_k = 0  # Reset for sequential run

                self.log(f"  Starting sequential processing for k={k}...")
                for sub_divisor in generate_sub_divisors_for_k():
                    num_divisors_processed_for_k += 1
                    winnable_res, _, _, _ = EWD(
                        sub_divisor.graph, sub_divisor, optimized=False
                    )
                    self.log(
                        f"    Processed (k={k}, item {num_divisors_processed_for_k}): Divisor {sub_divisor.degrees_to_str()} -> Winnable: {winnable_res}"
                    )
                    if not winnable_res:
                        any_unwinnable_found_for_k = True
                        self.log(
                            f"    Found unwinnable divisor {sub_divisor.degrees_to_str()} for k={k}."
                        )
                        break
                self.log(f"  Sequential processing finished for k={k}.")

            if any_unwinnable_found_for_k:
                self.log(
                    f"  For k={k}, an unwinnable configuration was found. Rank: {k-1}"
                )
                self._rank_value = k - 1
                return self
            else:
                self.log(
                    f"  All {num_divisors_processed_for_k} processed configurations for k={k} were winnable. Incrementing k."
                )
                k += 1
                # Loop continues for the next k

    def get_log_summary(self) -> str:
        """
        Get a complete log of the rank calculation process.

        Returns:
            str: A string containing all log messages from the calculation.
                 If no logs are available, returns "No calculation logs available."

        Example:
            >>> result = rank(divisor)
            >>> print(result.get_log_summary())
        """
        if not self.logs:
            return "No calculation logs available."

        return "\n".join(self.logs)


def rank(divisor: CFDivisor, optimized: bool = False) -> CFRank:
    """
    Calculate the rank of a given divisor.

    In divisor theory, the rank r(D) of a divisor D is defined as the largest integer r
    such that D-E is equivalent to an effective divisor for all effective divisors E of
    degree r. If D is not equivalent to an effective divisor, then r(D) = -1.

    The rank is computed as follows:

    1. If EWD(divisor) is not winnable, return -1.
    2. Starting with k = 1, consider all effective divisors E of degree k.
    3. For each such divisor E, check if D-E is winnable using the EWD algorithm. These checks
       are performed in parallel for a given k.
    4. If all checks for the current k are winnable, increment k and repeat step 2.
    5. Otherwise (if any check for D-E returns not winnable), the rank is k-1.
    
    Args:
        divisor: The CFDivisor object for which to calculate the rank.
        optimized: Whether to use optimized rank calculation. (default: False)
                   If True, theoretical shortcuts like Corollary 4.4.3 from
                   Dhyey Mavani's thesis will be used when applicable to speed up
                   calculations. The log will indicate when these optimizations are used.

    Returns:
        CFRank: An object with the calculated rank accessible via .rank property
                and calculation logs accessible via .logs attribute. One can also
                access the full log summary using .get_log_summary().

    Example:
        >>> result = rank(divisor)
        >>> print(f"Rank: {result.rank}")
        >>> print(result.get_log_summary())
    """
    return CFRank()._calculate_rank(divisor, optimized)


def r(divisor : CFDivisor, optimized: bool = False) -> int:
    """
    Calculate the rank of the given divisor, as in the funciton "rank." This funcion returns only the
    rank itself, as an integer, without the logs. Implemented as a wrapper around "rank."

    Args:
        divisor: The CFDivisor object for which to calculate the rank.
        optimized: Whether to use optimized rank calculation. (default: False)
                   If True, theoretical shortcuts like Corollary 4.4.3 from
                   Dhyey Mavani's thesis will be used when applicable to speed up
                   calculations. The log will indicate when these optimizations are used.

    Returns:
        int: The rank of the divisor.

    Example:
        >>> result = r(divisor)
        >>> print(f"Rank: {result}")
    """
    return CFRank()._calculate_rank(divisor, optimized).rank
