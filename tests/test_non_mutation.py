"""Regression tests: computations must not mutate caller-owned objects.

Only the explicit move methods of ``CFDivisor`` and ``CFConfig`` may change a
divisor in place. Every algorithm, predicate, and helper exercised here must
leave the divisor, graph, and other inputs it receives untouched, and copies
made by the package must stay attached to the caller's ``CFGraph`` object.
"""
import pytest

from chipfiring import (
    CFConfig,
    CFDivisor,
    CFGraph,
    CFLaplacian,
    CFOrientation,
    CFiringScript,
    DharAlgorithm,
    EWD,
    EWDVisualizer,
    GonalityDharAlgorithm,
    GreedyAlgorithm,
    is_q_reduced,
    is_winnable,
    linear_equivalence,
    q_reduction,
    q_reduction_with_root,
    r,
    rank,
)
from chipfiring.CFGonality import CFGonality, gonality, play_gonality_game
from chipfiring.CFGonalityDhar import enhanced_dhar_gonality_test


def degree_snapshot(divisor):
    return {vertex.name: degree for vertex, degree in divisor.degrees.items()}


def divisor_snapshot(divisor):
    return degree_snapshot(divisor), divisor.get_total_degree()


def graph_snapshot(graph):
    return (
        sorted(vertex.name for vertex in graph.vertices),
        sorted(
            (a.name, b.name, valence)
            for a in graph.graph
            for b, valence in graph.graph[a].items()
        ),
        {vertex.name: valence for vertex, valence in graph.vertex_total_valence.items()},
        graph.total_valence,
    )


@pytest.fixture
def sequence_graph():
    return CFGraph(
        {"Alice", "Bob", "Charlie", "Elise"},
        [
            ("Alice", "Bob", 1),
            ("Bob", "Charlie", 1),
            ("Charlie", "Elise", 1),
            ("Alice", "Elise", 2),
            ("Alice", "Charlie", 1),
        ],
    )


@pytest.fixture
def indebted_divisor(sequence_graph):
    return CFDivisor(
        sequence_graph,
        [("Alice", 2), ("Bob", -3), ("Charlie", 4), ("Elise", -1)],
    )


# --- DharAlgorithm --------------------------------------------------------------


@pytest.mark.parametrize(
    "action",
    [
        lambda dhar: dhar.run(),
        lambda dhar: dhar.send_debt_to_q(),
        lambda dhar: dhar.get_maximal_legal_firing_set(),
        lambda dhar: dhar.legal_set_fire(dhar.run()[0]),
    ],
    ids=["run", "send_debt_to_q", "get_maximal_legal_firing_set", "legal_set_fire"],
)
def test_dhar_algorithm_does_not_mutate_input(sequence_graph, indebted_divisor, action):
    before = divisor_snapshot(indebted_divisor)
    graph_before = graph_snapshot(sequence_graph)

    dhar = DharAlgorithm(sequence_graph, indebted_divisor, "Bob")
    action(dhar)

    assert divisor_snapshot(indebted_divisor) == before
    assert graph_snapshot(sequence_graph) == graph_before


def test_dhar_working_divisor_is_a_same_graph_copy(sequence_graph, indebted_divisor):
    dhar = DharAlgorithm(sequence_graph, indebted_divisor, "Bob")

    assert dhar.configuration.divisor is not indebted_divisor
    assert dhar.configuration.divisor.graph is sequence_graph
    assert dhar.configuration.divisor == indebted_divisor


def test_dhar_run_is_repeatable_on_the_same_input(sequence_graph, indebted_divisor):
    first, _ = DharAlgorithm(sequence_graph, indebted_divisor, "Bob").run()
    second, _ = DharAlgorithm(sequence_graph, indebted_divisor, "Bob").run()

    assert first == second


def test_gonality_dhar_algorithm_does_not_mutate_input():
    graph = CFGraph({"0", "1", "2", "3"}, [("0", "1", 1), ("1", "2", 1), ("2", "3", 1), ("3", "0", 1)])
    divisor = CFDivisor(graph, [("0", 1), ("1", -1)])
    before = divisor_snapshot(divisor)

    dhar = GonalityDharAlgorithm(graph, divisor, "0")
    dhar.test_strategy(["1", "2"])
    dhar.gonality_lower_bound()
    dhar.run()

    assert divisor_snapshot(divisor) == before


# --- Copies keep graph identity -------------------------------------------------


def test_greedy_algorithm_divisor_shares_caller_graph(sequence_graph, indebted_divisor):
    algorithm = GreedyAlgorithm(sequence_graph, indebted_divisor)
    before = divisor_snapshot(indebted_divisor)

    winnable, _ = algorithm.play()

    assert winnable is True
    assert algorithm.divisor.graph is sequence_graph
    assert divisor_snapshot(indebted_divisor) == before
    assert linear_equivalence(indebted_divisor, algorithm.divisor)


def test_cfconfig_copy_shares_caller_graph(sequence_graph, indebted_divisor):
    config = CFConfig(indebted_divisor, "Bob")
    duplicate = config.copy()

    assert duplicate.divisor is not indebted_divisor
    assert duplicate.divisor.graph is sequence_graph
    assert duplicate == config


def test_ewd_q_reduced_divisor_shares_caller_graph(sequence_graph, indebted_divisor):
    _, reduced, _, _ = EWD(sequence_graph, indebted_divisor, q_name="Bob")

    assert reduced.graph is sequence_graph
    assert linear_equivalence(indebted_divisor, reduced)


# --- Computations leave inputs untouched ----------------------------------------


def _full_orientation(graph):
    pairs = []
    seen = set()
    for a in sorted(graph.vertices):
        for b in sorted(graph.graph[a]):
            key = tuple(sorted((a.name, b.name)))
            if key not in seen:
                seen.add(key)
                pairs.append((a.name, b.name))
    return CFOrientation(graph, pairs)


@pytest.mark.parametrize(
    "compute",
    [
        lambda g, d: EWD(g, d),
        lambda g, d: EWD(g, d, optimized=True),
        lambda g, d: EWD(g, d, visualize=True, q_name="Bob"),
        lambda g, d: is_winnable(d),
        lambda g, d: q_reduction(d),
        lambda g, d: q_reduction_with_root(d, q_name="Alice"),
        lambda g, d: is_q_reduced(d, q_name="Bob"),
        lambda g, d: linear_equivalence(d, d + CFDivisor(g, [("Alice", 1)]) - CFDivisor(g, [("Bob", 1)])),
        lambda g, d: rank(d),
        lambda g, d: rank(d, optimized=True),
        lambda g, d: r(d),
        lambda g, d: CFConfig(d, "Bob").is_superstable(),
        lambda g, d: CFConfig(d, "Bob").is_legal_set_firing({"Alice", "Charlie"}),
        lambda g, d: CFLaplacian(g).apply(d, CFiringScript(g, {"Alice": 1, "Bob": -2})),
        lambda g, d: _full_orientation(g).divisor(),
        lambda g, d: _full_orientation(g).canonical_divisor(),
        lambda g, d: -d,
        lambda g, d: 3 * d,
        lambda g, d: d.remove_vertex("Elise"),
        lambda g, d: CFDivisor.from_dict(d.to_dict()),
        lambda g, d: play_gonality_game(g, 2, CFDivisor(g, [("Alice", 2)]), "Bob"),
        lambda g, d: CFGonality(g).test_n_chip_strategy(2, CFDivisor(g, [("Alice", 1), ("Bob", 1)])),
    ],
    ids=[
        "EWD", "EWD-optimized", "EWD-visualize", "is_winnable", "q_reduction",
        "q_reduction_with_root", "is_q_reduced", "linear_equivalence", "rank",
        "rank-optimized", "r", "is_superstable", "is_legal_set_firing", "laplacian-apply",
        "orientation-divisor", "canonical-divisor", "neg", "rmul", "remove_vertex",
        "dict-roundtrip", "play_gonality_game", "test_n_chip_strategy",
    ],
)
def test_public_computations_do_not_mutate_inputs(sequence_graph, indebted_divisor, compute):
    before = divisor_snapshot(indebted_divisor)
    graph_before = graph_snapshot(sequence_graph)

    compute(sequence_graph, indebted_divisor)

    assert divisor_snapshot(indebted_divisor) == before
    assert graph_snapshot(sequence_graph) == graph_before


def test_gonality_on_triangle_does_not_mutate_graph():
    graph = CFGraph({"A", "B", "C"}, [("A", "B", 1), ("B", "C", 1), ("A", "C", 1)])
    before = graph_snapshot(graph)

    result = gonality(graph)
    enhanced_dhar_gonality_test(graph, "A")

    assert result.gonality == 2
    assert graph_snapshot(graph) == before


def test_ewd_visualizer_history_is_a_true_snapshot_sequence(sequence_graph, indebted_divisor):
    _, reduced, _, visualizer = EWD(sequence_graph, indebted_divisor, visualize=True, q_name="Bob")

    snapshots = [degree_snapshot(step["divisor"]) for step in visualizer.history]

    assert snapshots[0] == degree_snapshot(indebted_divisor)
    assert snapshots[-1] == degree_snapshot(reduced)
    assert len(set(tuple(sorted(s.items())) for s in snapshots)) > 1


def test_visualizer_step_is_independent_of_later_mutation(sequence_graph, indebted_divisor):
    visualizer = EWDVisualizer()
    orientation = CFOrientation(sequence_graph, [("Alice", "Bob")])
    visualizer.add_step(indebted_divisor, orientation, q="Bob")
    stored = degree_snapshot(visualizer.history[0]["divisor"])

    indebted_divisor.lending_move("Charlie")

    assert degree_snapshot(visualizer.history[0]["divisor"]) == stored
