# Example drivers

This directory contains runnable examples for the repository. The first two
non-interactive drivers have saved expected-output files in `expected/`.

- `graph_orientation_example.py` is a non-interactive driver with expected console output in `expected/graph_orientation_example.txt`.
- `example_sequence_vs_laplacian.py` is a non-interactive driver with expected console output in `expected/example_sequence_vs_laplacian.txt`.
- `ewd_visualization_example.py` launches the interactive EWD visualization.
- `paper_chain_of_cycles.py` reproduces the paper's 1024-case genus-5
  chain-of-cycles experiment. The full default run can take several hours;
  use `python examples/paper_chain_of_cycles.py --limit 2` for a smoke test.
  Pass `--lengths 2,3,4,5` to choose the cycle lengths included in the
  five-cycle product.

From the repository root, run the two deterministic drivers and compare their
output with:

```sh
make check-example-outputs
```

The command exits nonzero if either saved output changes or if the two-case
chain-of-cycles smoke test disagrees with the expected gonality formula.
