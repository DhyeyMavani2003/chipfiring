# Changelog

All notable changes to this project are documented in this file.

## [1.1.4] - Unreleased

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

### Changed

- Add an optional `q_name` parameter to `EWD`, `q_reduction`, and
  `is_q_reduced`; omitting it preserves the minimum-degree default.
- Make automatic source selection deterministic by breaking degree ties with
  the vertex name.
- Centralize graph connectivity checks on `CFGraph.is_connected`.
- Correct and stabilize package docstrings and doctest examples.
- Include documentation, examples, tests, and test data in source distributions.
- Move project documentation to a standard root `README.md` and keep wheels
  limited to the importable `chipfiring` package.

### Added

- Regression tests for debt concentration, API non-mutation, explicit source
  selection, optimized-rank parity, parallel rank evaluation, empty and
  disconnected graphs, long greedy borrowing sequences, and large integers.
- A reproducible chain-of-cycles driver and saved-output example checks.
- CI verification for executable docstrings, saved examples, source and wheel
  builds, package metadata, and an installed-wheel import smoke test.
