# pysat: optimisation through RC2

## Change

The integration declared `optimization: false` and refused any submission with an
objective, which left 52 problems blocked for it. A submission may now return a
`pysat.formula.WCNF`: hard clauses are the constraints, soft clauses the objective,
and the runner solves it with `RC2Stratified` from `pysat.examples.rc2` over Glucose
4.2. A `CNF`, or a `WCNF` without soft clauses, is still solved by Glucose alone.

Files: `solvers/pysat/run.py`, `metadata.yaml` (no `optimization: false`; solver
`glucose42, RC2`; paradigms `sat`, `maxsat`), `readiness_test.py`, the readiness
record, `tests/fixtures/model_pysat.py`, the `pysat` entry in
`MAXIMIZATION_SWAPS` in `tests/test_solvers.py`, and the modelling skill
(`SKILL.md`, `sources.md`, `evals/evals.json`).

## Runner behaviour

- A model is emitted only when `compute()` returns one, which RC2 does only after
  proving the optimum. An interrupted search returns `None` and ends as `timeout`
  with the detail "the optimum was not proven".
- Enumeration blocks the declared outputs with a hard clause and stops at the first
  answer that costs more than the optimum.
- RC2 returns only variables that occur in the formula; the model is padded to the
  pool's top variable before `Integer.decode`.
- An objective returned as a third value is refused (execution error).
- The SIGALRM budget now raises a dedicated `BudgetExceeded`, reported as
  `timeout` rather than as an error. The first readiness run after the RC2 change
  had `timeout_cleanup` false once; after this change it passed on three runs.

## Why stratified

On knapsack json:3 (Burkardt P07, 15 items) plain `RC2` did not prove the optimum
in 178 s (attempt-001, execution_timeout on json:3). `RC2Stratified` proved it in
0.13 s inside the image, and the same model bytes were accepted on all 5
instances, each under 1 s (attempt-002). Probe scripts: `rc2probe.py`,
`rc2probe2.py` (scratchpad, run in the image, not candidate code).

## Evidence

- `build.log`: image builds.
- `readiness-check.log`, `solvers/pysat/readiness-result.json`: 15 checks true,
  including minimization, maximization, optimal_enumeration, suboptimal_rejected,
  rejects_objective_tuple and optimization_timeout.
- `test_solvers.log`: metadata tests plus the container `test_pilots` and
  `test_maximization` for pysat, with `DCP_CONTAINER_TESTS=1`: 7 passed.
- `generation.skills validate --project solvers/pysat/skills/pysat`: passed.

## Not done

The skill's new behavioural eval (`objective-as-soft-clauses`) was not run by a
separate agent. The other integrations' pilots were not rerun: no shared runner
file changed.
