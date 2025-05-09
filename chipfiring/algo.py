from .CFGraph import CFGraph
from .CFDivisor import CFDivisor
from .CFDhar import DharAlgorithm

def EWD(graph: CFGraph, divisor: CFDivisor) -> bool:
    """
    Determine if a graph is EWD using the EWD algorithm.
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
    unburnt_vertices = dhar.run()

    while len(unburnt_vertices) > 0:
        unburnt_vertices = dhar.run()
        dhar.legal_set_fire(unburnt_vertices)
    
    # 3. If the degree of q is non-negative, then the graph is winnable
    deg_q = divisor.get_total_degree() - dhar.configuration.get_total_degree()
    if deg_q >= 0:
        return True
    else:
        return False
    
if __name__ == "__main__":
    vertices = {"Alice", "Bob", "Charlie", "Elise"}
    edges = [
        ("Alice", "Bob", 1),
        ("Bob", "Charlie", 1),
        ("Charlie", "Elise", 1),
        ("Alice", "Elise", 2),
        ("Alice", "Charlie", 1)
    ]

    initial_degrees = [("Alice", 2), ("Bob", -3), ("Charlie", 4), ("Elise", -1)]

    graph = CFGraph(vertices, edges)
    divisor = CFDivisor(graph, initial_degrees)

    print(EWD(graph, divisor))