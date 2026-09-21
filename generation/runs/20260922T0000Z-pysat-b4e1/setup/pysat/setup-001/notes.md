# Setup: pysat

PySAT (python-sat), solving CNF with Glucose 4.2.

## Outcome

Ready. All nine required checks pass; `optimization: false` swaps the two
optimisation checks for `unsupported_optimization`.

## Files created

`solvers/pysat/` with `metadata.yaml`, `Dockerfile`, `run.py`, `dcp_sat.py`
(the modelling surface), `readiness_test.py`, `readiness.json` and the skill
bundle. Plus `tests/fixtures/model_pysat.py` and its registration in
`tests/test_solvers.py`, and one line in the README.

`tests/test_solvers.py` also gained a `satisfaction_only` helper: the pilot and
maximization cases need an objective, which this integration refuses, so they
are skipped for any integration whose metadata sets `optimization: false`.

## Versions

- base `python:3.12.11-slim-bookworm` by digest
- `python-sat[pblib]` 1.9.dev15; pypblib compiled in the image because it ships
  no wheel for 3.12, with the compiler dropped in the same layer
- image identity at readiness: `sha256:75d37f12e4d61604b8108e1cd3d0e8126fe18d88e1702f1d96201b37a665e110`

## The instance-binding decision

The submission reads the instance dict, like the other Python integrations. The
conversion that matters here is not JSON to data but data to clauses, which is
what `dcp_sat` does.

## Problems hit, and the fix

- **CaDiCaL cannot be interrupted.** PySAT raises `NotImplementedError` for
  limited solve on CaDiCaL and Lingeling. With CaDiCaL the runner could not stop
  its own search: a 14-into-13 pigeonhole ran past the 60s budget until the
  evaluator killed the container. Switched to Glucose 4.2, which stops within a
  tenth of a second of the interrupt, as do Minisat, Maplesat and MergeSat.
- **A Python signal handler cannot preempt a C extension.** The budget is
  enforced with the solver's own interrupt from a timer thread; SIGALRM now
  covers only the clause-building phase.
- `pypblib` needs a C++ compiler at install time.

## Capabilities and limits

Satisfaction and enumeration only. An objective is refused explicitly rather
than dropped, because the evaluator does not consult the `optimization` flag and
would otherwise compare a merely feasible answer against the reference optimum.
Integer variables are one-hot, so a wide domain is expensive; there is no
multiplication, division, modulo, element or cumulative.
