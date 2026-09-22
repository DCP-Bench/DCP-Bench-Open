# Sources for `pysat`

Documentation this skill's instructions were written from. Add an entry whenever
a claim here comes from a specific page or version.

- <https://pysathq.github.io/> — PySAT 1.9.dev15, the distribution the image
  installs.
- <https://pysathq.github.io/docs/html/api/card.html> and
  <https://pysathq.github.io/docs/html/api/pb.html> — `CardEnc` and `PBEnc`.
- <https://pysathq.github.io/docs/html/api/integer.html> — `pysat.integer`,
  the finite-domain layer submissions use for integer variables.
- `solvers/pysat/run.py` and `Dockerfile` in this repository — the contract
  this skill describes.

Every claim below was checked by running it inside the integration image, not
taken from documentation alone.

- **`pysat.integer` is the framework's own integer layer.** `Integer(name, lb,
  ub, encoding=...)` and `IntegerEngine(vars=..., vpool=...)` clausify direct,
  order or coupled domain encodings and translate linear constraints into
  pseudo-Boolean ones. An earlier version of this integration shipped a
  repository-local one-hot layer instead; this one does the same job, from the
  framework, with two more encodings.
- Its module docstring calls it "experimental" and "intentionally lightweight",
  and says it is not full-featured. It carries `add_linear`,
  `add_alldifferent`, `add_equal` and `add_not_equal`, and nothing else global.
- **The "experimental" label is about its user propagator, which this
  integration does not use.** The module's own worked example ends in
  `solver.connect_propagator(eng)`, so the propagator looks like the way in;
  `clausify()` is the other path and compiles every linear constraint with
  `CardEnc.atmost(seqcounter)` or `PBEnc.atmost(best)`. The runner takes a
  `CNF` and solves it with Glucose, so no propagator is ever connected.
  Checked by enumerating every solution the clausified CNF admits against
  brute force over the same domains, on five constraint shapes including
  weighted and negative coefficients: the sets matched exactly.
- `add_alldifferent`, `add_equal` and `add_not_equal` read `.vpool` off their
  arguments, so a `LinearExpr` raises `AttributeError: 'LinearExpr' object has
  no attribute 'vpool'`. Expressions go through `add_linear`.
- `IntegerEngine` inherits `add_constraint` from `BooleanEngine`, which accepts
  only `('linear', ...)` and `('parity', ...)` tuples and asserts on anything
  else. It is not the entry point for an integer constraint.
- **`PBEnc` accepts negative weights.** `PBEnc.equals` over
  `[3, -1, -2, 5, -5, 4]` with bound 0 gave `[3, -1, -2]`, summing to zero.
  Shifting terms to keep weights non-negative, which the previous version did,
  is unnecessary.
- `Integer.equals(value)` returns the literal for "this variable takes that
  value", which is what enumeration blocks on, and `Integer.decode(model)`
  reads the value back out of a solver model.
- **CaDiCaL and Lingeling cannot be interrupted.** PySAT raises
  `NotImplementedError: Limited solve is currently unsupported` for limited
  solve on both, so a hard instance runs until the evaluator kills the
  container. Glucose, Minisat, Maplesat and MergeSat all stop within a tenth of
  a second, and the runner uses Glucose 4.2.
- **The runner's SIGALRM and its solver interrupt must not be armed for the
  same instant.** They raced, and a SIGALRM that won surfaced as
  `execution_error: Runner execution budget exceeded` instead of the `timeout`
  the runner reports for itself. The interrupt is now pulled half a second
  forward.
- Pigeonhole refutation times with `Integer` plus `add_alldifferent` under
  Glucose 4.2: 12 into 11 takes 4.5 s, 13 into 12 takes 11.0 s, 14 into 13
  takes 24.6 s, 15 into 14 takes 70.9 s. The `timeout_cleanup` check uses 13
  into 12.
