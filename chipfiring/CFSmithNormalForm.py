"""Smith Normal Form computation for integer matrices.

This module provides an implementation of the Smith Normal Form (SNF) for
integer matrices, used to compute structural invariants of chip-firing groups
(Jacobian and Picard groups), and to test linear equivalence of divisors
algebraically without resorting to chip-firing dynamics.

The Smith Normal Form of an integer matrix A (m x n) is a diagonal matrix
D (m x n) such that there exist unimodular integer matrices U (m x m) and
V (n x n) with::

    U @ A @ V = D

and the diagonal entries d_1, d_2, ..., d_r of D (where r = min(m, n)) satisfy
d_i >= 0, d_1 | d_2 | ... | d_k, and d_{k+1} = ... = d_r = 0, where k is the
rank of A. The non-zero d_i are called the *elementary divisors* (or
*invariant factors*) of A.
"""
from __future__ import annotations
from typing import List, Sequence, Tuple

import numpy as np


def _swap_rows(M: np.ndarray, i: int, j: int) -> None:
    if i != j:
        M[[i, j]] = M[[j, i]]


def _swap_cols(M: np.ndarray, i: int, j: int) -> None:
    if i != j:
        M[:, [i, j]] = M[:, [j, i]]


def smith_normal_form(
    matrix: Sequence[Sequence[int]],
) -> Tuple[List[List[int]], List[List[int]], List[List[int]]]:
    """Compute the Smith Normal Form of an integer matrix.

    Args:
        matrix: A two-dimensional sequence of integers representing the input
            matrix ``A`` of shape ``(m, n)``.

    Returns:
        A tuple ``(D, U, V)`` where ``D``, ``U``, and ``V`` are nested Python
        ``int`` lists such that ``U @ A @ V == D``, ``U`` is an
        ``m x m`` unimodular integer matrix, ``V`` is an ``n x n`` unimodular
        integer matrix, and ``D`` is the ``m x n`` Smith Normal Form of ``A``
        (diagonal with non-negative entries satisfying the divisibility chain
        ``D[0,0] | D[1,1] | ...``, followed by zeros).

    Example:
        >>> D, U, V = smith_normal_form([[2, 4, 4], [-6, 6, 12], [10, -4, -16]])
        >>> D
        [[2, 0, 0], [0, 6, 0], [0, 0, 12]]
    """
    if len(matrix) == 0:
        return [], [], []

    m = len(matrix)
    n = len(matrix[0])
    for row in matrix:
        if len(row) != n:
            raise ValueError("All rows of the input matrix must have the same length.")

    # Use object dtype for exact (arbitrary-precision) integer arithmetic.
    D = np.array([[int(x) for x in row] for row in matrix], dtype=object)
    U = np.eye(m, dtype=object)
    V = np.eye(n, dtype=object)

    for k in range(min(m, n)):
        while True:
            # 1. Find the non-zero entry with smallest absolute value in
            #    D[k:, k:] and move it to position (k, k).
            best_i, best_j = -1, -1
            best_val = None
            for i in range(k, m):
                for j in range(k, n):
                    v = D[i, j]
                    if v != 0:
                        av = abs(v)
                        if best_val is None or av < best_val:
                            best_val = av
                            best_i, best_j = i, j

            if best_val is None:
                # Submatrix is entirely zero; this and all subsequent
                # diagonal entries are zero.
                break

            _swap_rows(D, k, best_i)
            _swap_rows(U, k, best_i)
            _swap_cols(D, k, best_j)
            _swap_cols(V, k, best_j)

            # 2. Reduce column k below the diagonal using row operations.
            changed = False
            for i in range(k + 1, m):
                if D[i, k] != 0:
                    q = D[i, k] // D[k, k]
                    if q != 0:
                        D[i, :] = D[i, :] - q * D[k, :]
                        U[i, :] = U[i, :] - q * U[k, :]
                    if D[i, k] != 0:
                        # A non-zero remainder appeared smaller than the
                        # current pivot; we need another pass.
                        changed = True

            # 3. Reduce row k to the right of the diagonal using column ops.
            for j in range(k + 1, n):
                if D[k, j] != 0:
                    q = D[k, j] // D[k, k]
                    if q != 0:
                        D[:, j] = D[:, j] - q * D[:, k]
                        V[:, j] = V[:, j] - q * V[:, k]
                    if D[k, j] != 0:
                        changed = True

            if changed:
                # Re-pick the pivot since smaller residuals appeared.
                continue

            # 4. Ensure D[k, k] divides every entry of the remaining
            #    submatrix; if not, add the offending row to row k and retry.
            divisor = D[k, k]
            non_div_row = -1
            for i in range(k + 1, m):
                for j in range(k + 1, n):
                    if D[i, j] % divisor != 0:
                        non_div_row = i
                        break
                if non_div_row != -1:
                    break

            if non_div_row == -1:
                # Make the pivot positive and move on.
                if D[k, k] < 0:
                    D[k, :] = -D[k, :]
                    U[k, :] = -U[k, :]
                break

            D[k, :] = D[k, :] + D[non_div_row, :]
            U[k, :] = U[k, :] + U[non_div_row, :]

    D_list = [[int(D[i, j]) for j in range(n)] for i in range(m)]
    U_list = [[int(U[i, j]) for j in range(m)] for i in range(m)]
    V_list = [[int(V[i, j]) for j in range(n)] for i in range(n)]
    return D_list, U_list, V_list


def elementary_divisors(matrix: Sequence[Sequence[int]]) -> List[int]:
    """Return the (positive) elementary divisors of an integer matrix.

    Args:
        matrix: A two-dimensional sequence of integers.

    Returns:
        The list of non-zero diagonal entries of the Smith Normal Form of
        ``matrix``, in the order ``d_1, d_2, ..., d_k`` with
        ``d_1 | d_2 | ... | d_k``.

    Example:
        >>> elementary_divisors([[2, 4, 4], [-6, 6, 12], [10, -4, -16]])
        [2, 6, 12]
    """
    D, _, _ = smith_normal_form(matrix)
    diag: List[int] = []
    for i in range(min(len(D), len(D[0]) if D else 0)):
        if D[i][i] != 0:
            diag.append(D[i][i])
    return diag
