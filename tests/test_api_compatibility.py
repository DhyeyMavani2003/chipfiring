import pytest

from chipfiring.CFCombinatorics import (
    gonality_theoretical_bounds,
    icosahedron_dhars_burning_algorithm,
    icosahedron_egg_cut_number,
    icosahedron_lemma_3_subgraph_bounds,
)
from chipfiring.CFGraph import CFGraph
from chipfiring.CFPlatonicSolids import (
    octahedron,
    verify_icosahedron_gonality,
    verify_icosahedron_theoretical_bounds_consistency,
    verify_octahedron_gonality,
)


def test_legacy_bound_and_egg_cut_keys_remain_available():
    assert "trivial_bound" in gonality_theoretical_bounds(CFGraph({"v"}, []))
    assert "scramble_bound" in gonality_theoretical_bounds(octahedron())
    assert icosahedron_egg_cut_number()["contributes_to_gonality"] is True
    assert "scramble_bound" in verify_octahedron_gonality()["theoretical_bounds"]


def test_deprecated_icosahedron_schema_remains_available():
    with pytest.deprecated_call():
        subgraph_data = icosahedron_lemma_3_subgraph_bounds()
    with pytest.deprecated_call():
        proof_data = icosahedron_dhars_burning_algorithm()

    assert subgraph_data["lemma_statement"]
    assert subgraph_data["critical_subgraphs"][0]["max_outdegree"] >= 8
    assert proof_data["debt_free_divisor_exists"]["construction"]
    assert proof_data["no_lower_degree_divisor"]["reason"]
    assert isinstance(proof_data["burning_sequences"][0]["burning_rounds"], int)


def test_legacy_icosahedron_verification_schema_remains_available():
    results = verify_icosahedron_gonality()
    assert results["gonality"] == 9
    assert results["dhars_burning_algorithm"]["gonality"] == 9
    assert results["comprehensive_bounds"]["exact_gonality"] == 9
    assert results["scramble_theory"]["egg_cut_number"]["contributes_to_gonality"]
    assert results["scramble_vs_gonality"]["conclusion"]
    assert verify_icosahedron_theoretical_bounds_consistency()[
        "dhars_result_consistent"
    ]
