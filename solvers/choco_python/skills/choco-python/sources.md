# Sources for `choco-python`

Documentation this skill's instructions were written from. Add an entry whenever
a claim here comes from a specific page or version.

- <https://pychoco.readthedocs.io/en/latest/> — pychoco reference, accessed
  2026-09-16
- <https://pypi.org/project/pychoco/0.2.1/> — the exact wheel this image
  installs; it bundles the Choco native library, so the image needs no JVM
- <https://choco-solver.org/docs/> — Choco 4 solver documentation, for the
  meaning of the constraints pychoco exposes
- `solvers/choco_python/run.py` and `Dockerfile` in this repository — the
  submission contract this skill describes

Every call in the API tables was exercised inside the built image during the
setup recorded at `generation/runs/20260916T091550-4d71/setup/choco_python/`,
not taken from documentation alone. A probe posted each one on a throwaway model
and reported which raised.

- Confirmed present and postable: `arithm` in both its three- and five-argument
  forms, `sum`, `scalar`, `all_different`, `all_different_except_0`,
  `all_equal`, `element` over both integer tables and variable tables, `count`,
  `global_cardinality`, `among`, `absolute`, `distance`, `div`, `mod`, `times`,
  `square`, `pow`, `min`, `max`, `sort`, `circuit`, `table`, `lex_less`,
  `lex_less_eq`, `increasing`, `decreasing`, `diff_n`, `cumulative`, `not_`,
  `and_`, `or_`, and both `Constraint.reify()` and `Constraint.reify_with(b)`.
- **Corrected against a first draft of this skill**: the methods are `sum`,
  `min` and `max`, not `sum_`, `min_` and `max_`. The trailing underscore
  belongs only to `and_`, `or_` and `not_`, which would otherwise shadow Python
  builtins. The first three raised `AttributeError` when probed.
- `element` takes the value first and the index third:
  `element(value, table, index, offset=0)`.
- `min` and `max` take the result variable first:
  `min(result, vars)`.
- `intvar` accepts either `(lb, ub)` or an explicit list of values.
- A `BoolVar` reads back through `get_value()` as a Python `bool`; an `IntVar`
  reads back as `int`. The runner relies on this and rejects anything else.
- `solver.limit_time("...ms")` stops the search at the limit: a probe that
  enumerated a deliberately huge space returned after 2.00s against a `"2s"`
  limit, having emitted 918489 solutions.
- pychoco 0.2.1 exposes no "search exhausted" or "stop criterion met" flag on
  the solver — the public surface is `solve`, `find_solution`,
  `find_all_solutions`, `find_optimal_solution`, `find_all_optimal_solutions`,
  `get_solution_count`, `limit_time` and the search-strategy setters. That is
  why `run.py` distinguishes exhaustion from a timeout by elapsed time, and why
  the skill warns that a model finishing right at the budget is reported as a
  timeout.
- `find_optimal_solution(variable, maximize=...)` returns a `Solution` whose
  value is read with `get_int_val(variable)`. Because Choco establishes
  optimality only by completing its branch and bound, `run.py` treats a run that
  consumed its whole budget as unproven rather than optimal.
- Choco enumerates distinct assignments of every variable, so a free auxiliary
  variable yields several solutions that share their declared outputs. The
  integration's readiness check pins this: a model with an unconstrained
  auxiliary variable, asked for ten solutions on an instance with three distinct
  outputs, is accepted with exactly three checked.
