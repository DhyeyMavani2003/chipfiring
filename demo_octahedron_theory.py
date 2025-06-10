#!/usr/bin/env python3
"""
Quick Demo: Using the Octahedron Theory Implementation

This script demonstrates how to use the newly implemented theoretical functions
from the octahedron section of "Chip-firing on the Platonic solids".
"""

from chipfiring.CFPlatonicSolids import octahedron
from chipfiring.CFCombinatorics import (
    independence_number,
    minimum_degree,
    maximum_degree,
    bramble_order_lower_bound,
    complete_multipartite_gonality,
    gonality_theoretical_bounds,
    is_bipartite
)

def demo_theoretical_functions():
    print("🔬 OCTAHEDRON THEORY FUNCTIONS DEMO")
    print("=" * 50)
    
    # Create the octahedron graph
    graph = octahedron()
    print(f"📊 Graph: Octahedron K_{{2,2,2}} with {len(graph.vertices)} vertices")
    
    # Basic graph properties
    print("\n🧮 Basic Properties:")
    print(f"   • Min degree: {minimum_degree(graph)}")
    print(f"   • Max degree: {maximum_degree(graph)}")
    print(f"   • Is bipartite: {is_bipartite(graph)}")
    print(f"   • Independence number: {independence_number(graph)}")
    
    # Theoretical bounds
    print("\n📏 Theoretical Bounds:")
    bounds = gonality_theoretical_bounds(graph)
    print(f"   • Independence upper bound: {bounds['independence_upper_bound']}")
    print(f"   • Minimum degree bound: {bounds['minimum_degree_bound']}")
    print(f"   • Bramble order bound: {bounds['bramble_order_bound']}")
    print(f"   • Final bounds: [{bounds['lower_bound']}, {bounds['upper_bound']}]")
    
    # Complete multipartite formula
    print("\n🧩 Complete Multipartite Formula:")
    print(f"   • K_{{2,2,2}} gonality: {complete_multipartite_gonality([2, 2, 2])}")
    print(f"   • K_{{3,4}} gonality: {complete_multipartite_gonality([3, 4])}")
    print(f"   • K_5 gonality: {complete_multipartite_gonality([5])}")
    
    # Bramble construction
    print("\n🌿 Bramble Theory:")
    bramble_bound = bramble_order_lower_bound(graph)
    print(f"   • Bramble order: {bramble_bound}")
    print(f"   • Treewidth lower bound: {bramble_bound - 1}")
    
    print(f"\n✨ Result: The octahedron has gonality = {bounds['upper_bound']}")
    print("=" * 50)

if __name__ == "__main__":
    demo_theoretical_functions()
