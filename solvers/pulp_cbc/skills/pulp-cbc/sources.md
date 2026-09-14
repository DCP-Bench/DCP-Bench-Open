# Sources for `pulp-cbc`

Documentation this skill's instructions were written from. Add an entry whenever
a claim here comes from a specific page or version.

- <https://coin-or.github.io/pulp/technical/pulp.html> — PuLP API reference, accessed 2026-09-14
- <https://coin-or.github.io/pulp/> — PuLP user guide, accessed 2026-09-14
- <https://pypi.org/project/PuLP/3.3.2/> — PuLP 3.3.2, the version pinned in the integration image, which ships the CBC binary it calls

Every API claim was checked by running PuLP 3.3.2 inside the integration image,
not taken from documentation alone:

- `x * y` and `x * x` raise `TypeError: Non-constant expressions cannot be
  multiplied`, and `abs(x)` raises `TypeError`, which is why every non-linear
  pattern in the skill is given an encoding instead.
- A second bare expression added to a problem overwrites the objective and warns
  `Overwriting previously set objective`.
- `problem.objective` is `None` until one is set, which is what lets the runner
  tell a satisfaction model from an optimization one with no extra convention.
- A `Binary` variable reports `cat == 'Integer'` with bounds 0 and 1; an
  `Integer` variable created without bounds reports `lowBound`/`upBound` of
  `None`, which is the case the runner refuses to enumerate.
- `pulp.value()` returns floats (`1.0` for a binary at one), so declared outputs
  are rounded within 1e-6 and rejected otherwise.
- **CBC stopped on its time limit still reports `LpStatus[problem.status] ==
  'Optimal'`; only `problem.sol_status` separates `LpSolutionOptimal` from
  `LpSolutionIntegerFeasible`.** Measured on a 60-item knapsack with a 3 s
  limit. The runner reads `sol_status` for exactly this reason, and
  `solvers/pulp_cbc/readiness_test.py` has an `unproven_optimum` check that
  fails if that guard is ever removed.
