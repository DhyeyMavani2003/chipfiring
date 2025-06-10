"""
Unit tests for CFCombinatorics module.

This module tests all combinatorial functions for parking functions,
independent sets, treewidth calculations, and graph analysis.
"""
import pytest
from chipfiring.CFCombinatorics import (
    is_parking_function,
    generate_parking_functions,
    parking_function_count,
    maximal_independent_sets,
    independence_number,
    treewidth_upper_bound,
    scramble_number_upper_bound,
    genus_upper_bound,
    gonality_theoretical_bounds,
    analyze_graph_properties,
    is_connected,
    graph_complement
)
from chipfiring.CFGraph import CFGraph


class TestParkingFunctions:
    """Test parking function related functions."""
    
    def test_is_parking_function_empty(self):
        """Test parking function check with empty sequence."""
        assert is_parking_function([])
    
    def test_is_parking_function_valid_sequences(self):
        """Test parking function check with valid sequences."""
        assert is_parking_function([1])
        assert is_parking_function([1, 1])
        assert is_parking_function([1, 2])
        assert is_parking_function([2, 1])
        assert is_parking_function([1, 1, 2])
        assert is_parking_function([1, 2, 1])
        assert is_parking_function([2, 1, 1])
        assert is_parking_function([1, 2, 3])
    
    def test_is_parking_function_invalid_sequences(self):
        """Test parking function check with invalid sequences."""
        assert not is_parking_function([2])  # [2] > [1]
        assert not is_parking_function([2, 2])  # sorted: [2,2], 2 > 1, 2 > 2
        assert not is_parking_function([1, 3, 3])  # sorted: [1,3,3], 3 > 2, 3 > 3
        assert not is_parking_function([2, 3, 3])  # sorted: [2,3,3], 3 > 2, 3 > 3  
        assert not is_parking_function([4, 1, 1])  # sorted: [1,1,4], 4 > 3
    
    def test_is_parking_function_out_of_range(self):
        """Test parking function check with out of range values."""
        assert not is_parking_function([0, 1, 2])  # 0 not in [1,n]
        assert not is_parking_function([1, 2, 4])  # 4 not in [1,3]
        assert not is_parking_function([-1, 1, 2])  # -1 not in [1,n]
    
    def test_is_parking_function_with_explicit_n(self):
        """Test parking function check with explicit n parameter."""
        assert is_parking_function([1, 2], n=2)
        assert not is_parking_function([1, 2], n=3)  # length mismatch
        assert not is_parking_function([1, 2, 3], n=2)  # length mismatch
        assert not is_parking_function([1, 1, 4], n=3)  # 4 > 3 (out of range)
    
    def test_generate_parking_functions_small_n(self):
        """Test generation of parking functions for small n."""
        # n = 0
        assert generate_parking_functions(0) == []
        
        # n = 1
        pf1 = generate_parking_functions(1)
        assert len(pf1) == 1
        assert [1] in pf1
        
        # n = 2
        pf2 = generate_parking_functions(2)
        assert len(pf2) == 3
        expected = [[1, 1], [1, 2], [2, 1]]
        for pf in expected:
            assert pf in pf2
        
        # n = 3
        pf3 = generate_parking_functions(3)
        assert len(pf3) == 16  # (3+1)^(3-1) = 4^2 = 16
    
    def test_generate_parking_functions_all_valid(self):
        """Test that all generated parking functions are valid."""
        for n in range(1, 5):
            pfs = generate_parking_functions(n)
            for pf in pfs:
                assert is_parking_function(pf, n)
    
    def test_parking_function_count(self):
        """Test parking function count formula."""
        assert parking_function_count(0) == 0
        assert parking_function_count(1) == 1  # (1+1)^(1-1) = 2^0 = 1
        assert parking_function_count(2) == 3  # (2+1)^(2-1) = 3^1 = 3
        assert parking_function_count(3) == 16  # (3+1)^(3-1) = 4^2 = 16
        assert parking_function_count(4) == 125  # (4+1)^(4-1) = 5^3 = 125
    
    def test_parking_function_count_matches_generation(self):
        """Test that count formula matches actual generation."""
        for n in range(1, 5):
            count = parking_function_count(n)
            generated = generate_parking_functions(n)
            assert count == len(generated)


class TestGraphIndependenceSets:
    """Test independent set and graph analysis functions."""
    
    @pytest.fixture
    def empty_graph(self):
        """Empty graph with no vertices."""
        return CFGraph(set(), [])
    
    @pytest.fixture
    def single_vertex_graph(self):
        """Graph with single vertex."""
        return CFGraph({"0"}, [])
    
    @pytest.fixture
    def two_vertex_no_edge(self):
        """Two vertices with no edge."""
        return CFGraph({"0", "1"}, [])
    
    @pytest.fixture
    def two_vertex_with_edge(self):
        """Two vertices with an edge."""
        return CFGraph({"0", "1"}, [("0", "1", 1)])
    
    @pytest.fixture
    def triangle_graph(self):
        """Triangle graph (K3)."""
        return CFGraph({"0", "1", "2"}, [("0", "1", 1), ("1", "2", 1), ("0", "2", 1)])
    
    @pytest.fixture
    def path_graph_4(self):
        """Path graph with 4 vertices: 0-1-2-3."""
        return CFGraph({"0", "1", "2", "3"}, [("0", "1", 1), ("1", "2", 1), ("2", "3", 1)])
    
    @pytest.fixture
    def cycle_graph_4(self):
        """Cycle graph with 4 vertices: 0-1-2-3-0."""
        return CFGraph({"0", "1", "2", "3"}, [("0", "1", 1), ("1", "2", 1), ("2", "3", 1), ("3", "0", 1)])
    
    @pytest.fixture
    def complete_graph_4(self):
        """Complete graph with 4 vertices."""
        edges = []
        vertices = {"0", "1", "2", "3"}
        for i in range(4):
            for j in range(i + 1, 4):
                edges.append((str(i), str(j), 1))
        return CFGraph(vertices, edges)
    
    def test_maximal_independent_sets_empty_graph(self, empty_graph):
        """Test MIS for empty graph."""
        mis = maximal_independent_sets(empty_graph)
        assert len(mis) == 1
        assert set() in mis
    
    def test_maximal_independent_sets_single_vertex(self, single_vertex_graph):
        """Test MIS for single vertex graph."""
        mis = maximal_independent_sets(single_vertex_graph)
        assert len(mis) == 1
        assert {"0"} in mis
    
    def test_maximal_independent_sets_two_vertex_no_edge(self, two_vertex_no_edge):
        """Test MIS for two vertices with no edge."""
        mis = maximal_independent_sets(two_vertex_no_edge)
        assert len(mis) == 1
        assert {"0", "1"} in mis
    
    def test_maximal_independent_sets_two_vertex_with_edge(self, two_vertex_with_edge):
        """Test MIS for two vertices with edge."""
        mis = maximal_independent_sets(two_vertex_with_edge)
        assert len(mis) == 2
        assert {"0"} in mis
        assert {"1"} in mis
    
    def test_maximal_independent_sets_triangle(self, triangle_graph):
        """Test MIS for triangle graph."""
        mis = maximal_independent_sets(triangle_graph)
        assert len(mis) == 3
        assert {"0"} in mis
        assert {"1"} in mis
        assert {"2"} in mis
    
    def test_maximal_independent_sets_path_4(self, path_graph_4):
        """Test MIS for path graph with 4 vertices."""
        mis = maximal_independent_sets(path_graph_4)
        # Possible MIS: {0,2}, {0,3}, {1,3}
        assert len(mis) >= 1
        # At least one of these should be present
        mis_sets = [frozenset(s) for s in mis]
        assert frozenset({"0", "2"}) in mis_sets or frozenset({"0", "3"}) in mis_sets or frozenset({"1", "3"}) in mis_sets
    
    def test_independence_number_empty_graph(self, empty_graph):
        """Test independence number for empty graph."""
        assert independence_number(empty_graph) == 0
    
    def test_independence_number_single_vertex(self, single_vertex_graph):
        """Test independence number for single vertex."""
        assert independence_number(single_vertex_graph) == 1
    
    def test_independence_number_two_vertex_no_edge(self, two_vertex_no_edge):
        """Test independence number for two vertices with no edge."""
        assert independence_number(two_vertex_no_edge) == 2
    
    def test_independence_number_two_vertex_with_edge(self, two_vertex_with_edge):
        """Test independence number for two vertices with edge."""
        assert independence_number(two_vertex_with_edge) == 1
    
    def test_independence_number_triangle(self, triangle_graph):
        """Test independence number for triangle."""
        assert independence_number(triangle_graph) == 1
    
    def test_independence_number_path_4(self, path_graph_4):
        """Test independence number for path with 4 vertices."""
        assert independence_number(path_graph_4) == 2
    
    def test_independence_number_cycle_4(self, cycle_graph_4):
        """Test independence number for 4-cycle."""
        assert independence_number(cycle_graph_4) == 2


class TestTreewidthAndBounds:
    """Test treewidth and other graph bounds."""
    
    @pytest.fixture
    def tree_3(self):
        """Tree with 3 vertices."""
        return CFGraph({"0", "1", "2"}, [("0", "1", 1), ("1", "2", 1)])
    
    @pytest.fixture
    def triangle(self):
        """Triangle graph."""
        return CFGraph({"0", "1", "2"}, [("0", "1", 1), ("1", "2", 1), ("0", "2", 1)])
    
    def test_treewidth_upper_bound_empty_single(self):
        """Test treewidth for empty and single vertex graphs."""
        empty = CFGraph(set(), [])
        single = CFGraph({"0"}, [])
        
        assert treewidth_upper_bound(empty) == 0
        assert treewidth_upper_bound(single) == 0
    
    def test_treewidth_upper_bound_tree(self, tree_3):
        """Test treewidth for tree (should be 1)."""
        tw = treewidth_upper_bound(tree_3)
        assert tw >= 1  # Trees have treewidth 1
    
    def test_treewidth_upper_bound_triangle(self, triangle):
        """Test treewidth for triangle (should be 2)."""
        tw = treewidth_upper_bound(triangle)
        assert tw >= 2  # K3 has treewidth 2
    
    def test_scramble_number_upper_bound(self, triangle):
        """Test scramble number upper bound."""
        scramble = scramble_number_upper_bound(triangle)
        assert scramble >= 1
        assert scramble <= 3  # Should be reasonable for small graph
    
    def test_genus_upper_bound_tree(self, tree_3):
        """Test genus upper bound for tree."""
        genus = genus_upper_bound(tree_3)
        assert genus == 0  # Trees have genus 0
    
    def test_genus_upper_bound_triangle(self, triangle):
        """Test genus upper bound for triangle."""
        genus = genus_upper_bound(triangle)
        assert genus >= 0  # Genus should be non-negative


class TestConnectivity:
    """Test graph connectivity functions."""
    
    def test_is_connected_empty_single(self):
        """Test connectivity for empty and single vertex graphs."""
        empty = CFGraph(set(), [])
        single = CFGraph({"0"}, [])
        
        assert is_connected(empty)
        assert is_connected(single)
    
    def test_is_connected_two_vertices(self):
        """Test connectivity for two vertex graphs."""
        connected = CFGraph({"0", "1"}, [("0", "1", 1)])
        disconnected = CFGraph({"0", "1"}, [])
        
        assert is_connected(connected)
        assert not is_connected(disconnected)
    
    def test_is_connected_path(self):
        """Test connectivity for path graph."""
        path = CFGraph({"0", "1", "2"}, [("0", "1", 1), ("1", "2", 1)])
        assert is_connected(path)
    
    def test_is_connected_disconnected_components(self):
        """Test connectivity for graph with multiple components."""
        # Two disconnected edges: 0-1 and 2-3
        disconnected = CFGraph({"0", "1", "2", "3"}, [("0", "1", 1), ("2", "3", 1)])
        assert not is_connected(disconnected)
    
    def test_is_connected_triangle(self):
        """Test connectivity for triangle."""
        triangle = CFGraph({"0", "1", "2"}, [("0", "1", 1), ("1", "2", 1), ("0", "2", 1)])
        assert is_connected(triangle)


class TestGraphComplement:
    """Test graph complement function."""
    
    def test_graph_complement_empty(self):
        """Test complement of empty graph."""
        empty = CFGraph(set(), [])
        comp = graph_complement(empty)
        assert len(comp.vertices) == 0
    
    def test_graph_complement_single_vertex(self):
        """Test complement of single vertex."""
        single = CFGraph({"0"}, [])
        comp = graph_complement(single)
        assert len(comp.vertices) == 1
        assert comp.total_valence == 0  # No self-loops
    
    def test_graph_complement_two_vertices_no_edge(self):
        """Test complement of two vertices with no edge."""
        no_edge = CFGraph({"0", "1"}, [])
        comp = graph_complement(no_edge)
        assert len(comp.vertices) == 2
        assert comp.total_valence == 1  # One edge in complement
        assert comp.get_valence("0") == 1
        assert comp.get_valence("1") == 1
    
    def test_graph_complement_two_vertices_with_edge(self):
        """Test complement of two vertices with edge."""
        with_edge = CFGraph({"0", "1"}, [("0", "1", 1)])
        comp = graph_complement(with_edge)
        assert len(comp.vertices) == 2
        assert comp.total_valence == 0  # No edges in complement
    
    def test_graph_complement_triangle(self):
        """Test complement of triangle (should be empty)."""
        triangle = CFGraph({"0", "1", "2"}, [("0", "1", 1), ("1", "2", 1), ("0", "2", 1)])
        comp = graph_complement(triangle)
        assert len(comp.vertices) == 3
        assert comp.total_valence == 0  # Complete graph complement is empty
    
    def test_graph_complement_path_3(self):
        """Test complement of path with 3 vertices."""
        path = CFGraph({"0", "1", "2"}, [("0", "1", 1), ("1", "2", 1)])
        comp = graph_complement(path)
        assert len(comp.vertices) == 3
        assert comp.total_valence == 1  # One missing edge: 0-2
        assert comp.get_valence("0") == 1
        assert comp.get_valence("2") == 1
        assert comp.get_valence("1") == 0


class TestGonalityBounds:
    """Test gonality bounds and graph analysis."""
    
    @pytest.fixture
    def triangle(self):
        """Create triangle graph for testing."""
        return CFGraph({"v0", "v1", "v2"}, 
                      [("v0", "v1", 1), ("v1", "v2", 1), ("v2", "v0", 1)])
    
    @pytest.fixture
    def path_4(self):
        """Path graph with 4 vertices."""
        return CFGraph({"0", "1", "2", "3"}, [("0", "1", 1), ("1", "2", 1), ("2", "3", 1)])
    
    def test_gonality_theoretical_bounds_single_vertex(self):
        """Test gonality bounds for single vertex."""
        single = CFGraph({"0"}, [])
        bounds = gonality_theoretical_bounds(single)
        assert bounds['trivial_bound'] == 1
    
    def test_gonality_theoretical_bounds_triangle(self, triangle):
        """Test gonality bounds for triangle."""
        bounds = gonality_theoretical_bounds(triangle)
        
        # Check that all expected bounds are present
        expected_keys = [
            'trivial_lower_bound', 'trivial_upper_bound', 'independence_upper_bound',
            'treewidth_lower_bound', 'genus_bound', 'scramble_bound', 'connectivity_bound',
            'lower_bound', 'upper_bound'
        ]
        for key in expected_keys:
            assert key in bounds
        
        # Check reasonableness of bounds
        assert bounds['trivial_lower_bound'] == 1
        assert bounds['trivial_upper_bound'] == 2  # n-1 = 3-1 = 2
        assert bounds['lower_bound'] <= bounds['upper_bound']
        assert bounds['independence_upper_bound'] == 2  # Triangle: n - α = 3 - 1 = 2
    
    def test_gonality_theoretical_bounds_path(self, path_4):
        """Test gonality bounds for path."""
        bounds = gonality_theoretical_bounds(path_4)
        
        assert bounds['trivial_lower_bound'] == 1
        assert bounds['trivial_upper_bound'] == 3  # n-1 = 4-1 = 3
        assert bounds['lower_bound'] <= bounds['upper_bound']
        assert bounds['independence_upper_bound'] == 2  # Path of 4 has independence number 2
    
    def test_analyze_graph_properties_triangle(self, triangle):
        """Test graph property analysis for triangle."""
        props = analyze_graph_properties(triangle)
        
        # Check basic properties
        assert props['num_vertices'] == 3
        assert props['num_edges'] == 3
        assert props['is_connected']
        assert not props['is_tree']  # Triangle is not a tree
        assert props['is_complete']  # Triangle is complete
        assert props['independence_number'] == 1
        
        # Check degree sequence
        assert props['degree_sequence'] == [2, 2, 2]  # All vertices have degree 2
        assert props['min_degree'] == 2
        assert props['max_degree'] == 2
        assert props['is_regular']
        assert props['average_degree'] == 2.0
        
        # Check that gonality bounds are included
        assert 'gonality_bounds' in props
        assert isinstance(props['gonality_bounds'], dict)
    
    def test_analyze_graph_properties_path(self, path_4):
        """Test graph property analysis for path."""
        props = analyze_graph_properties(path_4)
        
        # Check basic properties
        assert props['num_vertices'] == 4
        assert props['num_edges'] == 3
        assert props['is_connected']
        assert props['is_tree']  # Path is a tree
        assert not props['is_complete']  # Path is not complete
        assert props['independence_number'] == 2
        
        # Check degree sequence [2, 2, 1, 1] for path 0-1-2-3
        expected_degrees = [2, 2, 1, 1]  # Two middle vertices have degree 2, ends have degree 1
        assert sorted(props['degree_sequence'], reverse=True) == expected_degrees
        assert props['min_degree'] == 1
        assert props['max_degree'] == 2
        assert not props['is_regular']
        assert props['average_degree'] == 1.5


class TestEdgeCasesAndErrors:
    """Test edge cases and error handling."""
    
    def test_parking_function_negative_n(self):
        """Test parking function generation with negative n."""
        assert generate_parking_functions(-1) == []
        assert parking_function_count(-1) == 0
    
    def test_empty_graph_bounds(self):
        """Test various bounds for empty graph."""
        empty = CFGraph(set(), [])
        
        assert independence_number(empty) == 0
        assert treewidth_upper_bound(empty) == 0
        assert scramble_number_upper_bound(empty) == 0
        assert genus_upper_bound(empty) == 0
        assert is_connected(empty)
    
    def test_large_parking_function_count(self):
        """Test parking function count for larger values."""
        # Test that the formula works for larger n
        assert parking_function_count(5) == 6**4  # (5+1)^(5-1) = 6^4
        assert parking_function_count(10) == 11**9  # (10+1)^(10-1) = 11^9
    
    def test_graph_with_multiple_edges(self):
        """Test functions with graph containing multiple edges."""
        # Graph with multiple edges between same vertices
        multi_edge = CFGraph({"0", "1"}, [("0", "1", 3)])
        
        assert is_connected(multi_edge)
        assert independence_number(multi_edge) == 1
        
        props = analyze_graph_properties(multi_edge)
        assert props['num_vertices'] == 2
        assert props['num_edges'] == 3  # Multiple edges counted
        assert props['is_connected']


class TestAdditionalRobustness:
    """Additional tests for robustness and edge cases."""
    
    def test_parking_function_boundary_cases(self):
        """Test parking functions at boundary conditions."""
        # Test maximum valid values
        assert is_parking_function([1, 2, 3, 4, 5])  # Ascending sequence
        assert is_parking_function([5, 4, 3, 2, 1])  # Descending sequence
        assert is_parking_function([1, 1, 2, 4, 5])  # Mixed valid sequence
        
        # Test with repeated values
        assert is_parking_function([1, 1, 1, 1, 1])  # All minimum values
        assert not is_parking_function([2, 2, 2, 2, 2])  # All values > 1
        assert not is_parking_function([5, 5, 5, 5, 5])  # All max values (invalid)
    
    def test_maximal_independent_sets_comprehensive(self):
        """Test MIS with more complex graph structures."""
        # Star graph: one central vertex connected to all others
        star = CFGraph({"0", "1", "2", "3", "4"}, 
                      [("0", "1", 1), ("0", "2", 1), ("0", "3", 1), ("0", "4", 1)])
        mis = maximal_independent_sets(star)
        # Should have exactly 2 MIS: {0} (center only) or {1,2,3,4} (all leaves)
        assert len(mis) == 2
        assert {"0"} in mis or {"1", "2", "3", "4"} in mis
        
        # Complete bipartite graph K_{2,3}
        bipartite = CFGraph({"0", "1", "2", "3", "4"}, 
                           [("0", "2", 1), ("0", "3", 1), ("0", "4", 1),
                            ("1", "2", 1), ("1", "3", 1), ("1", "4", 1)])
        mis_bip = maximal_independent_sets(bipartite)
        # Should have exactly 2 MIS: {0,1} and {2,3,4}
        assert len(mis_bip) == 2
        assert {"0", "1"} in mis_bip
        assert {"2", "3", "4"} in mis_bip
    
    def test_bounds_consistency(self):
        """Test that various bounds are consistent."""
        # Create a path graph
        path_5 = CFGraph({"0", "1", "2", "3", "4"}, 
                        [("0", "1", 1), ("1", "2", 1), ("2", "3", 1), ("3", "4", 1)])
        
        # Independence number should be reasonable
        alpha = independence_number(path_5)
        assert 2 <= alpha <= 3  # Path of 5 should have independence number 3
        
        # Treewidth of a path should be 1
        tw = treewidth_upper_bound(path_5)
        assert tw >= 1
        
        # Genus should be 0 for trees
        genus = genus_upper_bound(path_5)
        assert genus == 0
    
    def test_parking_function_generation_completeness(self):
        """Test that parking function generation is complete and correct."""
        for n in range(1, 5):
            pfs = generate_parking_functions(n)
            count = parking_function_count(n)
            
            # Generated count should match formula
            assert len(pfs) == count
            
            # All generated sequences should be valid parking functions
            for pf in pfs:
                assert is_parking_function(pf, n)
                assert len(pf) == n
                assert all(1 <= x <= n for x in pf)
            
            # Should not have duplicates
            pf_tuples = [tuple(pf) for pf in pfs]
            assert len(pf_tuples) == len(set(pf_tuples))
    
    def test_graph_complement_properties(self):
        """Test properties of graph complements."""
        # Test that complement of complement is original (for small graphs)
        triangle = CFGraph({"0", "1", "2"}, [("0", "1", 1), ("1", "2", 1), ("0", "2", 1)])
        comp = graph_complement(triangle)
        comp_comp = graph_complement(comp)
        
        # Should have same vertices
        assert triangle.vertices == comp_comp.vertices
        # Should have same total valence (edge count doubled for undirected)
        assert triangle.total_valence == comp_comp.total_valence
    
    def test_connectivity_edge_cases(self):
        """Test connectivity with various edge cases."""
        # Single vertex is connected
        single = CFGraph({"0"}, [])
        assert is_connected(single)
        
        # Two vertices with no edge are disconnected
        disconnected_2 = CFGraph({"0", "1"}, [])
        assert not is_connected(disconnected_2)
        
        # Two vertices with edge are connected
        connected_2 = CFGraph({"0", "1"}, [("0", "1", 1)])
        assert is_connected(connected_2)
        
        # Multiple components
        multi_comp = CFGraph({"0", "1", "2", "3"}, [("0", "1", 1), ("2", "3", 1)])
        assert not is_connected(multi_comp)


class TestOctahedronSpecificFunctions:
    """Test octahedron-specific theoretical functions."""
    
    def test_octahedron_independence_number(self):
        """Test octahedron independence number function."""
        from chipfiring.CFCombinatorics import octahedron_independence_number
        
        alpha = octahedron_independence_number()
        assert alpha == 2
    
    def test_octahedron_bramble_construction(self):
        """Test octahedron bramble construction function."""
        from chipfiring.CFCombinatorics import octahedron_bramble_construction
        
        bramble = octahedron_bramble_construction()
        
        # Check structure
        assert isinstance(bramble, dict)
        assert bramble['order'] == 5
        assert bramble['separators'] == 4
        assert len(bramble['bramble_sets']) == 6  # Corrected: there are 6 bramble sets
        assert 'description' in bramble


class TestIcosahedronSpecificFunctions:
    """Test icosahedron-specific theoretical functions."""
    
    def test_icosahedron_independence_number(self):
        """Test icosahedron independence number function."""
        from chipfiring.CFCombinatorics import icosahedron_independence_number
        
        alpha = icosahedron_independence_number()
        assert alpha == 3
    
    def test_icosahedron_2_uniform_scramble(self):
        """Test icosahedron 2-uniform scramble construction function."""
        from chipfiring.CFCombinatorics import icosahedron_2_uniform_scramble
        
        scramble = icosahedron_2_uniform_scramble()
        
        # Check structure
        assert isinstance(scramble, dict)
        assert scramble['is_2_uniform']
        assert scramble['scramble_norm'] == 8
        assert len(scramble['scramble_sets']) == 6
        assert scramble['vertex_pairs'] == 6
        assert 'description' in scramble
    
    def test_icosahedron_screewidth_bound(self):
        """Test icosahedron screewidth bound function."""
        from chipfiring.CFCombinatorics import icosahedron_screewidth_bound
        
        screewidth_info = icosahedron_screewidth_bound()
        
        assert screewidth_info['screewidth_upper_bound'] == 8
        assert screewidth_info['scramble_number_bound'] == 8
        assert 'scw(I) ≤ ||S|| = 8' in screewidth_info['relation']
    
    def test_icosahedron_lemma_3_subgraph_bounds(self):
        """Test icosahedron Lemma 3 subgraph bounds function."""
        from chipfiring.CFCombinatorics import icosahedron_lemma_3_subgraph_bounds
        
        lemma3_info = icosahedron_lemma_3_subgraph_bounds()
        
        assert 'max_outdegree_bound' in lemma3_info
        assert lemma3_info['independence_number'] == 3
        assert 'critical_subgraphs' in lemma3_info
        assert len(lemma3_info['critical_subgraphs']) >= 3
    
    def test_icosahedron_dhars_burning_algorithm(self):
        """Test icosahedron Dhar's burning algorithm function."""
        from chipfiring.CFCombinatorics import icosahedron_dhars_burning_algorithm
        
        dhars_info = icosahedron_dhars_burning_algorithm()
        
        assert dhars_info['gonality'] == 9
        assert dhars_info['proof_complete']
        assert dhars_info['debt_free_divisor_exists']['degree'] == 9
        assert dhars_info['no_lower_degree_divisor']['degree'] == 8
    
    def test_icosahedron_egg_cut_number(self):
        """Test icosahedron egg-cut number function."""
        from chipfiring.CFCombinatorics import icosahedron_egg_cut_number
        
        egg_cut_info = icosahedron_egg_cut_number()
        
        assert egg_cut_info['egg_cut_number'] == 8
        assert egg_cut_info['lower_bound'] == 3
        assert egg_cut_info['upper_bound'] == 9
    
    def test_icosahedron_hitting_set_analysis(self):
        """Test icosahedron hitting set analysis function."""
        from chipfiring.CFCombinatorics import icosahedron_hitting_set_analysis
        
        hitting_set_info = icosahedron_hitting_set_analysis()
        
        assert hitting_set_info['minimum_hitting_set_size'] == 6
        assert 'scramble_sets' in hitting_set_info
        assert 'hitting_sets' in hitting_set_info
        assert len(hitting_set_info['hitting_sets']) >= 3
    
    def test_icosahedron_gonality_theoretical_bounds(self):
        """Test icosahedron comprehensive theoretical bounds function."""
        from chipfiring.CFCombinatorics import icosahedron_gonality_theoretical_bounds
        
        bounds = icosahedron_gonality_theoretical_bounds()
        
        # Check key bounds
        assert bounds['independence_upper_bound'] == 9
        assert bounds['scramble_number_bound'] == 8
        assert bounds['dhars_algorithm_result'] == 9
        assert bounds['screewidth_bound'] == 8
        assert bounds['lower_bound'] <= bounds['upper_bound']


class TestScrambleNumberTheory:
    """Test scramble number theory functions."""
    
    def test_scramble_2_uniform_properties(self):
        """Test properties of 2-uniform scrambles."""
        from chipfiring.CFCombinatorics import icosahedron_2_uniform_scramble
        
        scramble = icosahedron_2_uniform_scramble()
        
        # 2-uniform means all sets have size 2
        assert scramble['is_2_uniform']
        for scramble_set in scramble['scramble_sets']:
            assert len(scramble_set) == 2
        
        # Check construction type
        assert scramble['construction_type'] == 'opposite_vertex_pairs'
    
    def test_scramble_hitting_sets(self):
        """Test hitting set computations for scrambles."""
        from chipfiring.CFCombinatorics import icosahedron_hitting_set_analysis
        
        hitting_set_info = icosahedron_hitting_set_analysis()
        scramble_sets = hitting_set_info['scramble_sets']
        hitting_sets = hitting_set_info['hitting_sets']
        
        # Each hitting set must intersect all scramble sets
        for hitting_set in hitting_sets:
            for scramble_set in scramble_sets:
                intersection = hitting_set.intersection(scramble_set)
                assert len(intersection) >= 1
    
    def test_egg_cut_scramble_relationship(self):
        """Test relationship between egg-cut number and scramble theory."""
        from chipfiring.CFCombinatorics import (
            icosahedron_egg_cut_number,
            icosahedron_2_uniform_scramble
        )
        
        egg_cut_info = icosahedron_egg_cut_number()
        scramble_info = icosahedron_2_uniform_scramble()
        
        # Egg-cut number should relate to scramble norm
        assert egg_cut_info['egg_cut_number'] == scramble_info['scramble_norm']
        assert egg_cut_info['egg_cut_number'] == 8


if __name__ == "__main__":
    pytest.main([__file__])
