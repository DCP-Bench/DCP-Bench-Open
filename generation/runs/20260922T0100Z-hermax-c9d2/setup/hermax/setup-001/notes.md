# Setup: hermax

hermax 1.2.5, solving weighted MaxSAT with the EvalMaxSAT backend.

## Outcome

Ready. All ten required checks pass, including minimization and maximization.

## Files created

`solvers/hermax/` with `metadata.yaml`, `Dockerfile`, `run.py`,
`dcp_maxsat.py`, `readiness_test.py`, `readiness.json` and the skill bundle.
Plus `tests/fixtures/model_hermax.py` with its registration, and one line in
the README.

## Versions

- base `python:3.12.11-slim-bookworm` by digest
- `hermax` 1.2.5 (EvalMaxSAT), `python-sat[pblib]` 1.9.dev15 for encoders only
- image identity at readiness: `sha256:45332abc3cd053839b2abdf6d770a0a3140c84d32269fa6c48ae4a0561184bc0`

## How the objective works

A MaxSAT solver minimises the weight of broken soft clauses; it has no objective
expression. The submission hands over an integer variable, and the runner turns
its one-hot literals into soft units: minimising makes "not this value" cost
`value - min`, maximising makes it cost `max - value`. Exactly one value holds,
so the broken weight is the objective shifted by a constant. The modelling layer
gains a `link_*` family to tie that variable to an expression, which is the call
a model cannot omit.

## Problems hit, and the fix

- **No hermax backend can be time-bounded in process.** Both
  `solve(time_limit=...)` and `set_terminate` raise NotImplementedError, on
  EvalMaxSAT and on every other backend that would instantiate. The runner
  therefore supervises the search in a child process and kills it on budget,
  supplying the status the child never reached. Confirmed by a 16-into-15
  pigeonhole stopping at 60.8s against a 60s budget.
- `SolveStatus` is an IntEnum, so `str()` gives the number under Python 3.11+;
  comparisons use `.name`.
- EvalMaxSAT refutes pigeonhole far faster than the SAT integration's Glucose,
  so the timeout check needed a larger instance here.

## Capabilities and limits

Satisfaction, minimisation, maximisation and enumeration of optimal solutions.
Optimality is reported only on `SolveStatus.OPTIMUM`; a solution found without
that proof is a timeout, never an answer. Integer variables are one-hot, so the
objective's domain is its cost; there is no multiplication, division, modulo,
element or cumulative.
