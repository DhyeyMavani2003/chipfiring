#!/usr/bin/env python3
"""
Octahedron Theory Verification Script

This script demonstrates the implementation of theoretical concepts from 
"Chip-firing on the Platonic solids" by Beougher et al., specifically
the octahedron section theoretical results.

It verifies:
1. Independence number calculations and upper bounds for gonality (Theorem 1)
2. Bramble and treewidth theory for lower bounds on gonality (Theorem 2)  
3. Minimum degree bounds
4. Complete multipartite graph gonality formula
5. Octahedron-specific theoretical verification showing its gonality is exactly 4
"""

from chipfiring.CFPlatonicSolids import octahedron, verify_octahedron_gonality, verify_theoretical_bounds_consistency
from chipfiring.CFCombinatorics import (
    independence_number, minimum_degree, maximum_degree, bramble_order_lower_bound,
    octahedron_independence_number, octahedron_bramble_construction,
    complete_multipartite_gonality, gonality_theoretical_bounds, is_bipartite
)

def main():
    print("=" * 80)
    print("OCTAHEDRON THEORY VERIFICATION")
    print("Implementing concepts from 'Chip-firing on the Platonic solids'")
    print("=" * 80)
    
    # Generate octahedron graph
    print("\n1. Generating octahedron graph (K_{2,2,2})...")
    graph = octahedron()
    print(f"   Vertices: {len(graph.vertices)}")
    print(f"   Edges: {graph.total_valence}")  # total_valence is already the number of edges
    print(f"   Is bipartite: {is_bipartite(graph)}")
    
    # Test independence number (Theorem 1)
    print("\n2. Testing Theorem 1: gon(G) ≤ n - α(G)")
    alpha_computed = independence_number(graph)
    alpha_theoretical = octahedron_independence_number()
    independence_upper_bound = 6 - alpha_computed
    
    print(f"   Independence number α(G): {alpha_computed}")
    print(f"   Theoretical α(G): {alpha_theoretical}")
    print(f"   Independence upper bound (n - α): {independence_upper_bound}")
    print(f"   ✓ Independence numbers match: {alpha_computed == alpha_theoretical}")
    
    # Test bramble construction (Theorem 2)  
    print("\n3. Testing Theorem 2: tw(G) ≤ gon(G)")
    bramble_info = octahedron_bramble_construction()
    bramble_bound = bramble_order_lower_bound(graph)
    treewidth_lower = bramble_bound - 1  # bramble order = treewidth + 1
    
    print("   Bramble construction:")
    print(f"     - Bramble sets: {len(bramble_info['bramble_sets'])}")
    print(f"     - Bramble order: {bramble_info['order']}")
    print(f"     - Separators: {bramble_info['separators']}")
    print(f"   Treewidth lower bound: {treewidth_lower}")
    print(f"   ✓ Treewidth ≥ 4: {treewidth_lower >= 4}")
    
    # Test minimum degree bounds
    print("\n4. Testing minimum degree bounds: δ(G) ≤ tw(G) ≤ gon(G)")
    min_deg = minimum_degree(graph)
    max_deg = maximum_degree(graph)
    
    print(f"   Minimum degree δ(G): {min_deg}")
    print(f"   Maximum degree Δ(G): {max_deg}")
    print(f"   ✓ Regular graph: {min_deg == max_deg}")
    print(f"   ✓ δ(G) ≤ tw(G): {min_deg <= treewidth_lower}")
    
    # Test complete multipartite gonality formula
    print("\n5. Testing complete multipartite gonality formula")
    multipartite_gonality = complete_multipartite_gonality([2, 2, 2])
    print(f"   K_{{2,2,2}} gonality formula: {multipartite_gonality}")
    print("   Formula: n - min(partition) = 6 - 2 = 4")
    print(f"   ✓ Formula gives correct result: {multipartite_gonality == 4}")
    
    # Test theoretical bounds consistency
    print("\n6. Testing theoretical bounds consistency")
    bounds = gonality_theoretical_bounds(graph)
    
    print("   Bounds computed:")
    for bound_name, value in bounds.items():
        if 'bound' in bound_name:
            print(f"     - {bound_name}: {value}")
    
    print(f"   ✓ Lower ≤ Upper: {bounds['lower_bound'] <= bounds['upper_bound']}")
    print(f"   ✓ Independence bound = 4: {bounds['independence_upper_bound'] == 4}")
    print(f"   ✓ Minimum degree bound = 4: {bounds['minimum_degree_bound'] == 4}")
    print(f"   ✓ Bramble order bound ≥ 4: {bounds['bramble_order_bound'] >= 4}")
    
    # Complete verification
    print("\n7. Complete octahedron gonality verification")
    verification = verify_octahedron_gonality()
    
    print(f"   Theoretical gonality: {verification['gonality']}")
    print(f"   All theoretical bounds consistent: {verification['verification_passed']}")
    
    # Test all Platonic solids bounds
    print("\n8. Testing theoretical bounds consistency for all Platonic solids")
    consistency_results = verify_theoretical_bounds_consistency()
    
    print("   Platonic solids bounds consistency:")
    for solid, is_consistent in consistency_results.items():
        status = "✓" if is_consistent else "✗"
        print(f"     {status} {solid}: {is_consistent}")
    
    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    all_tests_passed = (
        alpha_computed == alpha_theoretical and
        treewidth_lower >= 4 and
        min_deg == max_deg == 4 and
        multipartite_gonality == 4 and
        bounds['independence_upper_bound'] == 4 and
        verification['verification_passed'] and
        all(consistency_results.values())
    )
    
    if all_tests_passed:
        print("🎉 ALL THEORETICAL CONCEPTS SUCCESSFULLY IMPLEMENTED!")
        print("\nImplemented features:")
        print("✓ Theorem 1: Independence number upper bound (gon(G) ≤ n - α(G))")
        print("✓ Theorem 2: Treewidth lower bound (tw(G) ≤ gon(G))")
        print("✓ Minimum degree bounds (δ(G) ≤ tw(G) ≤ gon(G))")
        print("✓ Complete multipartite gonality formula (gon(K_{n1,...,nk}) = n - min(ni))")
        print("✓ Octahedron gonality verification (gonality = 4)")
        print("✓ Bramble construction proving treewidth ≥ 4")
        print("✓ Theoretical bounds consistency for all Platonic solids")
    else:
        print("❌ Some theoretical concepts failed verification")
        
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
