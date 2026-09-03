# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Fixed

- Stop `DharAlgorithm` (and therefore `GonalityDharAlgorithm`) from rewriting
  the caller's divisor. The algorithm now works on a private copy that shares
  the caller's graph object and exposes it as `configuration.divisor`. Code
  that read the input divisor after `run()` to obtain the reduced state should
  read `configuration.divisor` instead.
- Keep `GreedyAlgorithm` and `CFConfig.copy` on the caller's `CFGraph` object
  instead of deep-copying the graph, so their results stay comparable with the
  original divisor.
- Compare graphs structurally in `linear_equivalence`. Divisors on
  independently constructed or deserialized copies of the same graph are no
  longer reported as inequivalent because the graph objects differ.
- Make `CFLaplacian.get_reduced_matrix` a pure query; it no longer inserts zero
  entries into the cached Laplacian rows.
- Accept single-pass iterables (generators, `zip`) as `CFDivisor` degrees
  instead of silently producing a zero divisor.

### Added

- `CFDivisor.copy` (with `copy.copy` support) returning an independent divisor
  on the same graph object.
- Structural `CFGraph` equality and hashing: two graphs are equal when they have
  the same vertex names and edge multiplicities.
- Regression tests asserting that the winnability, q-reduction, rank, gonality,
  Dhar, greedy, configuration, Laplacian, orientation, and visualizer routines
  leave their inputs unchanged, plus copy-semantics and graph-identity tests.

### Changed

- Document the by-reference semantics of `CFConfig`, the copy semantics of
  `DharAlgorithm` and `GreedyAlgorithm`, and the snapshot semantics of the EWD
  visualizer history.

## [1.1.4] - 2026-08-25

### Fixed

- Make debt concentration revisit vertices that become negative again, with a
  least-action termination argument and explicit connected-graph validation.
- Prevent `EWD`, `is_winnable`, `q_reduction`, and `is_q_reduced` from mutating
  the caller's divisor.
- Make `is_q_reduced` compare against the original divisor instead of an object
  already mutated in place.
- Apply the Riemann-Roch correction when optimized rank computes the rank of
  `K-D`, including the case where the complementary divisor is unwinnable.
- Replace the greedy solver's arbitrary move cap with the proven cumulative
  marked-vertex stopping criterion.
- Preserve arbitrary-precision Python integer coefficients after Laplacian
  application instead of coercing through fixed-width NumPy arrays, while using
  the sparse graph representation rather than dense matrix multiplication.
- Reject disconnected inputs before EWD shortcuts or the greedy solver can
  return an invalid result or fail to terminate.
- Restore the advertised parallel rank path by moving its worker to a picklable
  module-level function and counting completed candidates in the parent process.
- Treat every supported sequence type consistently in the chain-of-cycles
  gonality verifier.
- Correct complete-multipartite gonality to subtract the largest part, and
  handle the one-vertex complete graph consistently with the rank definition.
- Replace incorrect icosahedron scramble and proof placeholders with the
  all-edge scramble, computed hitting sets and cut data, exhaustive subgraph
  boundary checks, and clearly labeled literature-backed gonality data.
- Remove invalid generic gonality-bound implications and restrict the
  independence/treewidth aggregation to connected simple graphs.

### Changed

- Add an optional `q_name` parameter to `EWD`, `q_reduction`, and
  `is_q_reduced` while preserving the historical most-indebted default.
- Add `q_reduction_with_root` for callers that need the automatically selected
  root when checking the returned divisor.
- Make automatic source selection deterministic by breaking degree ties with
  the vertex name.
- Centralize graph connectivity checks on `CFGraph.is_connected`.
- Correct and stabilize package docstrings and doctest examples.
- Include documentation, examples, tests, and test data in source distributions.
- Move project documentation to a standard root `README.md` and keep wheels
  limited to the importable `chipfiring` package.
- Rename the chain-of-cycles example and use standalone terminology, semantic
  test names, and stable source attributions.
- Keep PyPI runtime dependencies limited to imported libraries and declare
  Python 3.8+ metadata explicitly.

### Added

- Regression tests for debt concentration, API non-mutation, explicit source
  selection, optimized-rank parity, parallel rank evaluation, empty and
  disconnected graphs, long greedy borrowing sequences, and large integers.
- A reproducible chain-of-cycles driver and saved-output example checks.
- CI verification for executable docstrings, saved examples, source and wheel
  builds, package metadata, and an installed-wheel import smoke test.
- A PEP 517 build-system declaration and complete source-distribution support
  for the documented Makefile, coverage, and Sphinx workflows.

### Deprecated

- Retain `icosahedron_dhars_burning_algorithm` and
  `icosahedron_lemma_3_subgraph_bounds` as compatibility wrappers. New code
  should use `icosahedron_gonality_proof_summary` and
  `icosahedron_subgraph_outdegree_bounds`.
