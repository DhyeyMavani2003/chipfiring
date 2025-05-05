#!/usr/bin/env python3

"""
Example demonstrating the equivalence between a sequence of 
set_fire operations and a single application of the Laplacian
with a net firing script.
"""

from chipfiring import CFGraph, CFDivisor, CFLaplacian, CFiringScript

def print_divisor_state(label: str, divisor: CFDivisor):
    """Helper function to print the current state of the divisor."""
    print(f"--- {label} ---")
    states = []
    for v in sorted(divisor.graph.vertices):
        states.append(f"{v.name}={divisor.degrees[v]}")
    print(", ".join(states))
    print(f"Total Degree: {divisor.get_total_degree()}")
    print("---")


def main():
    # 1. Define Graph
    vertices = {"Alice", "Bob", "Charlie", "Elise"}
    edges = [
        ("Alice", "Bob", 1),
        ("Bob", "Charlie", 1),
        ("Charlie", "Elise", 1),
        ("Alice", "Elise", 2),
        ("Alice", "Charlie", 1)
    ]
    graph = CFGraph(vertices, edges)
    print("Graph Created:")
    print(f"Vertices: {[v.name for v in sorted(graph.vertices)]}")
    print("Edges (with valence): A-B(1), B-C(1), C-E(1), A-E(2), A-C(1)")
    print("Valences: A={}, B={}, C={}, E={}".format(
        graph.get_valence("Alice"),
        graph.get_valence("Bob"),
        graph.get_valence("Charlie"),
        graph.get_valence("Elise")
    ))
    print("="*20)

    # 2. Define Initial Divisor
    initial_degrees = [("Alice", 2), ("Bob", -3), ("Charlie", 4), ("Elise", -1)]
    initial_divisor = CFDivisor(graph, initial_degrees)
    print_divisor_state("Initial State", initial_divisor)

    # 3. Demonstrate set_fire sequence
    print("Applying sequence of set_fire operations...")
    divisor_seq = CFDivisor(graph, initial_degrees) # Start with a fresh copy

    firing_set_1 = {"Alice", "Elise", "Charlie"}
    print(f"\nApplying set_fire({firing_set_1})...")
    divisor_seq.set_fire(firing_set_1)
    print_divisor_state("State after fire 1", divisor_seq)

    firing_set_2 = {"Alice", "Elise", "Charlie"}
    print(f"\nApplying set_fire({firing_set_2})...")
    divisor_seq.set_fire(firing_set_2)
    print_divisor_state("State after fire 2", divisor_seq)

    firing_set_3 = {"Bob", "Charlie"}
    print(f"\nApplying set_fire({firing_set_3})...")
    divisor_seq.set_fire(firing_set_3)
    final_state_seq = divisor_seq.degrees.copy()
    print_divisor_state("Final State after Sequence", divisor_seq)
    print("="*20)

    # 4. Reset divisor (conceptually, or use initial_divisor)
    # We will use the initial_divisor directly for the Laplacian calculation

    # 5. Define Equivalent Firing Script
    # Net effect of the sequence: Bob borrows 1, Charlie fires 1
    script_dict = {"Bob": -1, "Charlie": 1}
    firing_script = CFiringScript(graph, script_dict)
    print("Equivalent Net Firing Script:")
    print(firing_script.script)
    print("="*20)

    # 6. Create Laplacian
    laplacian = CFLaplacian(graph)
    print("Laplacian Created.")
    # Optional: Print matrix (can be large for bigger graphs)
    # matrix = laplacian._construct_matrix()
    # print(matrix)
    print("="*20)

    # 7. Apply Laplacian with the script
    print("Applying Laplacian with the net firing script...")
    divisor_lap = laplacian.apply(initial_divisor, firing_script)
    final_state_lap = divisor_lap.degrees.copy()
    print_divisor_state("Final State via Laplacian", divisor_lap)
    print("="*20)

    # 8. Compare Final States
    print("Comparing final states...")
    print(f"Sequence Final State: { {v.name: d for v, d in sorted(final_state_seq.items())} }")
    print(f"Laplacian Final State:{ {v.name: d for v, d in sorted(final_state_lap.items())} }")

    if final_state_seq == final_state_lap:
        print("\nSuccess! The final states from both methods are identical.")
    else:
        print("\nError! The final states do not match.")


if __name__ == "__main__":
    main() 