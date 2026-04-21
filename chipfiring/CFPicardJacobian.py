"""Picard and Jacobian groups of a chip-firing graph.

For a connected multigraph G with Laplacian L, viewed as a linear map
``L : Z^V -> Z^V``:

* The **Picard group** is ``Pic(G) = Z^V / Im(L)``, the group of divisors
  modulo the principal divisors.  The degree map ``deg : Z^V -> Z`` descends
  to a surjection ``Pic(G) -> Z`` with kernel the **Jacobian group**.
* The **Jacobian group** (also known as the *critical group* or
  *sandpile group*) is ``Jac(G) = Pic^0(G) = ker(deg) / Im(L)``.  Its order
  equals the number of spanning trees of ``G`` (the Matrix-Tree theorem).

The group structure is computed from the Smith Normal Form of the Laplacian
matrix: if the elementary divisors of ``L`` (in the ``|V|``-square SNF) are
``d_1 | d_2 | ... | d_{n-1}`` (with one trailing zero, since a connected
graph has rank ``n-1``), then::

    Jac(G) ~= Z/d_1 (+) Z/d_2 (+) ... (+) Z/d_{n-1}
    Pic(G) ~= Z (+) Jac(G)

(Trivial summands ``Z/1`` are dropped from the displayed structure.)
"""
from __future__ import annotations

from typing import List, Tuple

import numpy as np

from .CFDivisor import CFDivisor
from .CFGraph import CFGraph, Vertex
from .CFLaplacian import CFLaplacian
from .CFSmithNormalForm import smith_normal_form


def _laplacian_matrix(graph: CFGraph) -> Tuple[List[List[int]], List[Vertex]]:
    """Return the integer Laplacian matrix of ``graph`` and its vertex order."""
    laplacian = CFLaplacian(graph)
    ordered_vertices = sorted(list(graph.vertices), key=lambda v: v.name)
    n = len(ordered_vertices)
    L: List[List[int]] = [[0] * n for _ in range(n)]
    for i, v_row in enumerate(ordered_vertices):
        for j, v_col in enumerate(ordered_vertices):
            L[i][j] = int(laplacian.laplacian[v_row][v_col])
    return L, ordered_vertices


def _divisor_to_vector(divisor: CFDivisor, ordered_vertices: List[Vertex]) -> List[int]:
    return [int(divisor.degrees.get(v, 0)) for v in ordered_vertices]


def _is_in_image(
    diag: List[int], U: List[List[int]], b: List[int]
) -> bool:
    """Return True iff ``b`` lies in the image of a matrix whose SNF has
    diagonal ``diag`` and left-multiplier ``U`` (so ``U @ A @ V == diag``).

    ``A x = b`` is solvable in integers iff ``D y = U b`` is solvable, which
    holds iff each component of ``c = U @ b`` is divisible by the
    corresponding diagonal entry (and is zero where the diagonal entry is 0).
    """
    U_np = np.array(U, dtype=object)
    b_np = np.array(b, dtype=object)
    c = U_np @ b_np
    for i, d in enumerate(diag):
        ci = int(c[i])
        if d == 0:
            if ci != 0:
                return False
        else:
            if ci % d != 0:
                return False
    # Any extra rows of c (m > n) must be zero (no diagonal entry).
    for i in range(len(diag), len(c)):
        if int(c[i]) != 0:
            return False
    return True


class JacobianGroup:
    """The Jacobian (critical / sandpile) group of a chip-firing graph.

    The Jacobian group is the cokernel of the Laplacian restricted to
    degree-zero divisors.  For a connected graph ``G`` with Laplacian ``L``,
    this is isomorphic to the direct sum of cyclic groups whose orders are
    the non-zero elementary divisors of ``L`` (equivalently, of any reduced
    Laplacian ``L_q``).

    Args:
        graph: The underlying chip-firing graph.

    Example:
        >>> from chipfiring import CFGraph
        >>> g = CFGraph({"a", "b", "c"}, [("a", "b", 1), ("b", "c", 1), ("a", "c", 1)])
        >>> jac = JacobianGroup(g)
        >>> jac.order  # K_3 has 3 spanning trees
        3
        >>> jac.invariant_factors
        [3]
        >>> jac.structure()
        'Z/3Z'
    """

    def __init__(self, graph: CFGraph):
        self.graph = graph
        self._ordered_vertices: List[Vertex]
        self._L: List[List[int]]
        self._L, self._ordered_vertices = _laplacian_matrix(graph)
        self._D, self._U, self._V = smith_normal_form(self._L)
        # Diagonal entries of the SNF, in order.
        n = len(self._ordered_vertices)
        self._diag: List[int] = [self._D[i][i] for i in range(n)]

    @property
    def invariant_factors(self) -> List[int]:
        """Invariant factors of the Jacobian group.

        These are the non-zero elementary divisors of the Laplacian that are
        strictly greater than 1 (the ``Z/1`` summands are trivial and are
        omitted).
        """
        return [d for d in self._diag if d != 0 and d != 1]

    @property
    def order(self) -> int:
        """Order of the Jacobian group (the number of spanning trees of G).

        For a disconnected graph, the Jacobian (as defined here, the cokernel
        modulo a single ``Z`` factor) is infinite; in that case this method
        raises :class:`ValueError`.
        """
        zeros = sum(1 for d in self._diag if d == 0)
        if zeros > 1:
            raise ValueError(
                "Jacobian group is infinite; the underlying graph appears to "
                "be disconnected."
            )
        product = 1
        for d in self._diag:
            if d != 0:
                product *= d
        return product

    def structure(self) -> str:
        """Return a human-readable description of the group structure."""
        factors = self.invariant_factors
        if not factors:
            return "0"
        return " (+) ".join(f"Z/{d}Z" for d in factors)

    def contains(self, divisor: CFDivisor) -> bool:
        """Check whether a degree-zero divisor is the zero element of Jac(G).

        A divisor of degree 0 represents the identity element of ``Jac(G)``
        iff it lies in the image of the Laplacian, i.e. it is a principal
        divisor.

        Args:
            divisor: A divisor on the same graph as this Jacobian group.

        Returns:
            ``True`` if ``divisor`` has degree 0 and is principal, else
            ``False``.
        """
        if divisor.graph != self.graph:
            return False
        if divisor.get_total_degree() != 0:
            return False
        b = _divisor_to_vector(divisor, self._ordered_vertices)
        return _is_in_image(self._diag, self._U, b)

    def __len__(self) -> int:
        return self.order

    def __repr__(self) -> str:
        return f"JacobianGroup(order={self.order}, structure='{self.structure()}')"


class PicardGroup:
    """The Picard group of a chip-firing graph.

    For a connected graph ``G``, ``Pic(G) = Z^V / Im(L)`` is isomorphic to
    ``Z (+) Jac(G)``, where the ``Z`` factor is detected by the degree of a
    divisor.

    Args:
        graph: The underlying chip-firing graph.

    Example:
        >>> from chipfiring import CFGraph
        >>> g = CFGraph({"a", "b", "c"}, [("a", "b", 1), ("b", "c", 1), ("a", "c", 1)])
        >>> pic = PicardGroup(g)
        >>> pic.free_rank
        1
        >>> pic.torsion_order
        3
        >>> pic.structure()
        'Z (+) Z/3Z'
    """

    def __init__(self, graph: CFGraph):
        self.graph = graph
        self.jacobian = JacobianGroup(graph)

    @property
    def invariant_factors(self) -> List[int]:
        """Invariant factors of the torsion part of Pic(G).

        These coincide with the invariant factors of ``Jac(G)``.
        """
        return self.jacobian.invariant_factors

    @property
    def free_rank(self) -> int:
        """Rank of the free part of Pic(G).

        Equals the number of connected components of the graph (1 for any
        connected graph).
        """
        return sum(1 for d in self.jacobian._diag if d == 0)

    @property
    def torsion_order(self) -> int:
        """Order of the torsion subgroup of Pic(G), equal to ``|Jac(G)|``."""
        return self.jacobian.order

    def structure(self) -> str:
        """Return a human-readable description of the group structure."""
        free_part = " (+) ".join(["Z"] * self.free_rank) if self.free_rank else ""
        torsion_part = self.jacobian.structure()
        if torsion_part == "0":
            return free_part if free_part else "0"
        if not free_part:
            return torsion_part
        return f"{free_part} (+) {torsion_part}"

    def equivalent(self, divisor1: CFDivisor, divisor2: CFDivisor) -> bool:
        """Check whether two divisors define the same class in ``Pic(G)``.

        Equivalently, whether ``divisor1 - divisor2`` lies in the image of
        the Laplacian (i.e. is a principal divisor).

        Args:
            divisor1: First divisor.
            divisor2: Second divisor.

        Returns:
            ``True`` iff ``divisor1`` and ``divisor2`` are linearly
            equivalent.
        """
        if divisor1.graph != self.graph or divisor2.graph != self.graph:
            return False
        if divisor1.get_total_degree() != divisor2.get_total_degree():
            return False
        diff = divisor1 - divisor2
        b = _divisor_to_vector(diff, self.jacobian._ordered_vertices)
        return _is_in_image(self.jacobian._diag, self.jacobian._U, b)

    def __repr__(self) -> str:
        return (
            f"PicardGroup(free_rank={self.free_rank}, "
            f"torsion_order={self.torsion_order}, structure='{self.structure()}')"
        )
