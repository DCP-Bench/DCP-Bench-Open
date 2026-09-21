# Sources for `pysat`

Documentation this skill's instructions were written from. Add an entry whenever
a claim here comes from a specific page or version.

- <https://pysathq.github.io/docs/html/api/solvers.html> — the `Solver` API,
  including `solve_limited`, `interrupt` and `clear_interrupt`.
- <https://pysathq.github.io/docs/html/api/card.html> — `CardEnc` and the
  cardinality encodings behind `at_most`, `at_least` and `exactly`.
- <https://pysathq.github.io/docs/html/api/pb.html> — `PBEnc`, the
  pseudo-Boolean encoders behind every linear constraint here, which need
  `pypblib`.
- `solvers/pysat/dcp_sat.py`, `run.py` and `Dockerfile` in this repository — the
  contract this skill describes.

Every claim below was checked by running it inside the integration image during
the run recorded at `generation/runs/20260922T0000Z-pysat-b4e1`, not taken from
documentation alone.

- **CaDiCaL and Lingeling cannot be interrupted through PySAT.** Both raise
  `NotImplementedError: Limited solve is currently unsupported` from
  `interrupt()`. Glucose 4.2, Minisat 2.2, Maplesat and MergeSat 3 each stopped
  within a tenth of a second of the interrupt. The integration therefore solves
  with Glucose; with CaDiCaL a hard instance ran past the runner's own budget
  until the evaluator killed the container from outside.
- A Python `SIGALRM` handler cannot fire while the search is inside the solver's
  C extension, so the budget has to be enforced with the solver's own interrupt.
  The `SIGALRM` in `run.py` covers only the clause-building phase.
- The linear helpers were verified on a mixed instance: a `[-5, 5]` domain with
  `sum_eq(..., -3)`, coefficients `3` and `-2` in one `weighted_sum_eq`, a
  Boolean weighted sum containing a negative and a zero weight, a sparse domain
  through `int_from`, and `same`/`different` across domains that only partly
  overlap. All produced the expected assignment.
- `pypblib` ships no wheel for Python 3.12, so the image compiles it and drops
  the compiler again in the same layer.
- Pigeonhole is the reliable way to make this solver run long. How long depends
  sharply on the backend, so the figures are worth attaching to one: CaDiCaL
  refutes 13 pigeons into 12 holes in about 0.6 seconds and needs well over a
  minute for 14 into 13, while Glucose, which this integration actually uses,
  already exceeds two seconds on 13 into 12. That is what the
  `timeout_cleanup` check relies on.
