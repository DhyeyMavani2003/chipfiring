#!/usr/bin/env python3

from chipfiring import CFGraph, CFOrientation, CFDivisor

def main():
    # Create a simple graph with 4 vertices and multiple edges
    vertices = {"A", "B", "C", "D"}
    edges = [
        ("A", "B", 2),  # 2 edges between A and B
        ("B", "C", 1),  # 1 edge between B and C
        ("C", "D", 3),  # 3 edges between C and D
        ("D", "A", 1),  # 1 edge between D and A
    ]

    # Create the graph
    graph = CFGraph(vertices, edges)
    print("Graph created!")
    print(f"Total edges (counting multiplicity): {graph.total_valence}")
    print(f"Graph genus: {graph.get_genus()}")
    print(f"Valence of vertex A: {graph.get_valence('A')}")
    print()

    # Create an orientation of the graph
    # Orient some edges (not all need to be oriented)
    orientations = [
        ("A", "B"),  # Orient A->B
        ("C", "B"),  # Orient C->B
        ("C", "D"),  # Orient C->D
    ]
    orientation = CFOrientation(graph, orientations)
    print("Orientation created!")
    print(f"Edge A-B orientation: {orientation.get_orientation('A', 'B')}")
    print(f"Edge D-A orientation: {orientation.get_orientation('D', 'A')}")  # Should be None (unoriented)
    print(f"In-degree of B: {orientation.get_in_degree('B')}")   # Should be 3 (2 from A, 1 from C)
    print(f"Out-degree of C: {orientation.get_out_degree('C')}")  # Should be 4 (1 to B, 3 to D)
    print()

    # Create a divisor (chip configuration) on the graph
    # Place some chips at vertices
    degrees = [
        ("A", 3),  # 3 chips at A
        ("B", 1),  # 1 chip at B
        ("D", 2),  # 2 chips at D
    ]
    divisor = CFDivisor(graph, degrees)
    print("Divisor (chip configuration) created!")
    print(f"Chips at vertex A: {divisor.get_degree('A')}")
    print(f"Chips at vertex C: {divisor.get_degree('C')}")  # Should be 0
    print(f"Total chips: {divisor.get_total_degree()}")
    print()

if __name__ == "__main__":
    main() 