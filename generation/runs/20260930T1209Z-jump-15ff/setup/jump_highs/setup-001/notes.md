# jump_highs setup

New integration for JuMP on HiGHS: a model is Julia code that builds a JuMP
model, and HiGHS solves it as a mixed-integer linear program.

- Artifacts: `solvers/jump_highs/metadata.yaml`, `Dockerfile`, `run.py`,
  `driver.jl`, `Project.toml`, `Manifest.toml`, `readiness_test.py`, and the
  skill bundle `solvers/jump_highs/skills/jump/`. Wiring outside that
  directory: `tests/fixtures/model_jump.jl` with its `PILOTS` and
  `MAXIMIZATION_SWAPS` rows in `tests/test_solvers.py`; a `julia` row in
  `LANGUAGES`, `.jl` in `EXTENSION_LANGUAGE` and the highlight.js Julia grammar
  in `generate_site.py`; and the name in `README.md`.
- Versions: the official `julia:1.12-bookworm` image pinned by digest (Julia
  1.12.7), Debian's `python3` 3.11.2-1+b1 for the runner, and a Manifest that
  pins JuMP 1.32.0, HiGHS.jl 1.26.0, HiGHS_jll 1.15.1 and JSON 1.10.0. The
  packages are installed and precompiled at build time.
- Image built with `python -m evaluation.build jump_highs`:
  `sha256:1e2a7151692def217f9235986f443073a9894479efba40cbb756c1369ba67b6a`.

## Design

- The submission reads the instance as a `Dict{String, Any}` and returns
  `(model, outputs)`; the model carries its own objective. The driver attaches
  HiGHS with one thread, silence, the remaining time as the limit and a
  relative MIP gap of 0, so OPTIMAL is a proven optimum.
- Enumeration follows the PuLP integration: pin the objective at the optimum,
  then add a no-good cut over the integer variables behind the declared
  outputs. Those variables must be integer and bounded; otherwise the driver
  reports `unsupported`.
- The runtime depot path puts a writable depot in `/tmp` before the read-only
  one with the precompiled packages. A run with a read-only root recompiles
  nothing: package loading takes about 2.4 s and a first solve about 4.7 s.
- The driver writes its records to a file, and `run.py` stops the process
  at the budget less one second.
- Two driver bugs were found and fixed before readiness: Julia 1.12 warns when
  `build` is looked up in an older world, so the lookup goes through
  `invokelatest`; and JuMP refuses solution queries after the model changes,
  so a solution's values are read before its no-good cut is added.

## Evidence

- `probes/t1.jl` measured the load and first-solve times.
- `probes/api.jl` and `probes/api2.jl` back every claim in the skill: the MOI
  sets that bridge to MILP for HiGHS, indicator constraints, the constraints
  it rejects (`Reified`, products of variables, `Table` with an integer
  matrix), the JSON shapes, loop scope and variable-name reuse.
- The readiness models, run directly through the image, gave the expected
  records, and the isolation probe run as root with network reports an error,
  so it fails closed.
- `pilot-probe.py` runs the `test_pilots` and `test_maximization` cases for
  jump_highs: 7, 7 and 1 solutions checked, as those tests require.
- Readiness passed all twelve checks on the first certification run; the
  record is `solvers/jump_highs/readiness.json`.

## Not done

- The behavioural cases in `evals/evals.json` are specifications; none has
  been run by an independent agent.
