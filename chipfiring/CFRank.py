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


def _is_rank_candidate_winnable(sub_divisor: CFDivisor) -> bool:
    """Return whether a rank candidate is winnable in a worker process."""
    winnable, _, _, _ = EWD(
        sub_divisor.graph, sub_divisor, optimized=False
    )
    return winnable


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
        >>> from chipfiring import CFGraph, CFDivisor
        >>> graph = CFGraph({"v"}, [])
        >>> divisor = CFDivisor(graph, [("v", -1)])
        >>> result = rank(divisor)
        >>> result.rank
        -1
        >>> result.logs[-1]
        'Initial divisor is not winnable. So, rank: -1'
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
        riemann_roch_correction = None

        def store_working_rank(working_rank: int) -> None:
            """Store rank(D), correcting a rank(K-D) computation when necessary."""
            if riemann_roch_correction is None:
                self._rank_value = working_rank
                return

            self._rank_value = working_rank + riemann_roch_correction
            self.log(
                "Optimized mode: Applying the Riemann-Roch correction "
                "rank(D) = rank(K-D) + degree(D) + 1 - genus(G). "
                f"Corrected rank: {self._rank_value}"
            )

        # 1. Call EWD on the divisor; if unwinnable, return -1
        self.log("Step 1: Checking initial winnability through EWD algorithm...")
        initial_winnable, _, _, _ = EWD(graph, divisor, optimized=False)
        if not initial_winnable:
            self.log("Initial divisor is not winnable. So, rank: -1")
            self._rank_value = -1
            return self
        self.log("Initial divisor is winnable. Proceeding to step 2.")

        if optimized:
            self.log(
                "Optimized mode is enabled. Checking if we can apply theoretical shortcuts before proceeding."
            )

            D = self._divisor
            # Graph Riemann-Roch gives r(D) = deg(D) - g when deg(D) > 2g - 2.
            if D.get_total_degree() > 2 * graph.get_genus() - 2:
                self.log(
                    "Optimized mode: Graph Riemann-Roch gives rank(D) = "
                    "degree(D) - genus(G) when degree(D) > 2g-2; "
                    "skipping enumeration."
                )
                self._rank_value = D.get_total_degree() - graph.get_genus()
                return self

            # Check if the degree of (K-D) < degree of D, if so, run next step on (K-D)
            orientation = CFOrientation(graph, [])
            K = orientation.canonical_divisor()
            if (K - D).get_total_degree() < D.get_total_degree():
                self.log(
                    "Optimized mode: (K-D) has lower degree than D. Running next step on (K-D)."
                )
                self._divisor = K - D
                riemann_roch_correction = D.get_total_degree() + 1 - graph.get_genus()

                self.log(
                    "Optimized mode: Checking whether (K-D) is initially winnable."
                )
                complementary_winnable, _, _, _ = EWD(
                    graph, self._divisor, optimized=False
                )
                if not complementary_winnable:
                    self.log("Optimized mode: (K-D) is not winnable. So, rank(K-D): -1")
                    store_working_rank(-1)
                    return self
                self.log("Optimized mode: (K-D) is winnable. Proceeding to step 2.")
            else:
                self.log(
                    "Optimized mode: (K-D) has degree >= that of D. Running next step on D itself."
                )

        # 2. Sort the vertices by name
        sorted_vertices = sorted(list(graph.vertices), key=lambda v: v.name)
        worker_count = max(1, min(cpu_count(), len(sorted_vertices)))

        k = 1
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
            pool = None

            try:
                self.log(
                    f"  Starting parallel processing for k={k} "
                    f"with {worker_count} workers..."
                )
                pool = Pool(processes=worker_count)
                # The number of divisors can be large, so use imap_unordered for lazy evaluation
                results_iterator = pool.imap_unordered(
                    _is_rank_candidate_winnable,
                    generate_sub_divisors_for_k(),
                )

                for winnable_res in results_iterator:
                    num_divisors_processed_for_k += 1
                    self.log(
                        f"    Processed (k={k}, "
                        f"item {num_divisors_processed_for_k}): "
                        f"Winnable -> {winnable_res}"
                    )
                    if not winnable_res:
                        any_unwinnable_found_for_k = True
                        pool.terminate()
                        pool.join()
                        pool = None
                        break

                if pool is not None:
                    pool.close()
                    pool.join()
                    pool = None

                self.log(f"  Parallel processing finished for k={k}.")

            except Exception as e:
                if pool is not None:
                    pool.terminate()
                    pool.join()
                self.log(
                    f"  Multiprocessing failed for k={k}: {e}. Falling back to sequential execution."
                )
                any_unwinnable_found_for_k = False  # Reset for sequential run
                num_divisors_processed_for_k = 0  # Reset for sequential run

                self.log(f"  Starting sequential processing for k={k}...")
                for sub_divisor in generate_sub_divisors_for_k():
                    num_divisors_processed_for_k += 1
                    winnable_res = _is_rank_candidate_winnable(sub_divisor)
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
                rank_label = "rank(K-D)" if riemann_roch_correction is not None else "rank(D)"
                self.log(
                    f"  For k={k}, an unwinnable configuration was found. "
                    f"{rank_label}: {k-1}"
                )
                store_working_rank(k - 1)
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
            >>> from chipfiring import CFGraph, CFDivisor
            >>> graph = CFGraph({"v"}, [])
            >>> divisor = CFDivisor(graph, [("v", -1)])
            >>> result = rank(divisor)
            >>> "Initial divisor is not winnable" in result.get_log_summary()
            True
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
        optimized: Whether to use graph Riemann-Roch shortcuts when applicable.
                   The log indicates when an optimization is used.

    Returns:
        CFRank: An object with the calculated rank accessible via .rank property
                and calculation logs accessible via .logs attribute. One can also
                access the full log summary using .get_log_summary().

    Example:
        >>> from chipfiring import CFGraph, CFDivisor
        >>> graph = CFGraph({"v"}, [])
        >>> divisor = CFDivisor(graph, [("v", -1)])
        >>> result = rank(divisor)
        >>> result.rank
        -1
        >>> bool(result.logs)
        True
    """
    return CFRank()._calculate_rank(divisor, optimized)


def r(divisor : CFDivisor, optimized: bool = False) -> int:
    """
    Calculate the rank of the given divisor, as in the function ``rank``. This function returns only the
    rank itself, as an integer, without the logs. Implemented as a wrapper around "rank."

    Args:
        divisor: The CFDivisor object for which to calculate the rank.
        optimized: Whether to use graph Riemann-Roch shortcuts when applicable.
                   The log indicates when an optimization is used.

    Returns:
        int: The rank of the divisor.

    Example:
        >>> from chipfiring import CFGraph, CFDivisor
        >>> graph = CFGraph({"v"}, [])
        >>> divisor = CFDivisor(graph, [("v", -1)])
        >>> r(divisor)
        -1
    """
    return CFRank()._calculate_rank(divisor, optimized).rank
