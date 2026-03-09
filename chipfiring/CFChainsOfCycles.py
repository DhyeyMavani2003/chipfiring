from __future__ import annotations

import chipfiring as cf

"""
Constructs a basic chain of cycles graph, where each cycle is connected in sequence.

Each cycle is specified by its length in the `cycle_lengths` list. The cycles are connected such that
the attachment points are always at positions -1 and 0 of each cycle. Vertices are named as "z_{i+1}_{j}",
where `i` is the cycle index (starting from 0) and `j` is the position within the cycle.

Edges are created as follows:
- For cycles of length greater than 2, standard cycle edges are added with weight 1.
- For cycles of length 2, a single edge of weight 2 connects the two vertices.
- Each cycle (except the first) is connected to the previous cycle by an edge of weight 1 between
    the 0-th vertex of the current cycle and the last vertex of the previous cycle.

Parameters
----------
cycle_lengths : list of int
        A list of integers, each representing the length of a cycle in the chain.
        Each length must be an integer greater than or equal to 2.

Returns
-------
cf.CFGraph
        A chip-firing graph object representing the chain of cycles.

Raises
------
ValueError
        If any cycle length is not an integer greater than or equal to 2.

Examples
--------
>>> G = basicChain([3, 4, 5])
>>> print(G.vertices)
>>> print(G.edges)
"""


# Basic chain of cycles, in which the attachment points are always positions -1 and 0, and only cycle lenghts are specifiied.
def basicChain(cycle_lengths: list[int]):
    if not all(isinstance(n, int) and n >= 2 for n in cycle_lengths):
        raise ValueError(
            "All cycle lengths must be integers greater than or equal to 2."
        )
    vertices = {f"z_{i+1}_{j}" for i, n in enumerate(cycle_lengths) for j in range(n)}
    # edges = [(f"z_{i+1}_{j}",f"z_{i+1}_{(j+1)%n}",1) for i,n in enumerate(cycle_lengths) for j in range(n)]
    edges = []
    for i, n in enumerate(cycle_lengths):
        if n == 2:
            edges.append((f"z_{i+1}_0", f"z_{i+1}_1", 2))
        else:
            for j in range(n):
                edges.append((f"z_{i+1}_{j}", f"z_{i+1}_{(j+1)%n}", 1))
    for i, n in enumerate(cycle_lengths):
        if i == 0:
            continue
        edges.append((f"z_{i}_0", f"z_{i+1}_{n-1}", 1))
    return cf.CFGraph(vertices, edges)
