# Setup notes: z3_python

Built the Z3 Python integration from official Z3 documentation (recorded in the
modelling skill's `sources.md`). One setup attempt; no repair needed.

## Order of work, stated plainly

The integration was built and its readiness recorded **before** this run and
this setup-attempt directory existed, so the snapshot here was taken after the
work rather than before it. `skills/solver-setup` was not modified at any point
in this session, so the snapshot is byte-identical to the version that guided
the work — but the usual "freeze first, then work" ordering was not followed,
and that is worth knowing when reading this record.

## What was produced

- `solvers/z3_python/metadata.yaml` — key set copied from the pilot
  integrations; `enumeration: true`, no `optimization` key, so the readiness
  checklist required minimization and maximization.
- `solvers/z3_python/run.py` — the runner protocol. It does not add a `kind` to
  `runner/runtime.py`: touching that file would change code shared with the four
  existing images and would mean re-certifying `cpmpy_python`. It imports
  `emit`, `finish`, `flatten` and `mapped` from it instead.
- `solvers/z3_python/Dockerfile` — pins `z3-solver==5.1.0.0` and deliberately
  does **not** install `runner/requirements.txt`: `runtime.py` imports its
  solver stacks lazily, so this image needs neither CPMpy nor OR-Tools and stays
  small. `z3-solver` was not added to the shared requirements file.
- `solvers/z3_python/readiness_test.py` and the recorded readiness evidence.
- `solvers/z3_python/skills/z3-python/` — the modelling skill bundle.

## Decisions worth recording

The submission contract is `build(instance) -> (constraints, outputs)` with an
optional third element `("minimize"|"maximize", expression)`. The objective is
passed to the runner rather than set by the candidate on a `z3.Optimize`,
because the runner must prove optimality and `Optimize.check()` returning `sat`
does not establish it. The runner instead compares `Optimize.lower(handle)` with
`Optimize.upper(handle)` and reports `timeout` when they differ, then enumerates
optimal solutions from a plain `Solver` with the objective pinned to the proven
value.

Verified against Z3 5.1.0 while writing the skill: `Abs` exists, `Max`/`Min`/
`Element`/`AllDifferent` do not, Python `max`/`min`/`any`/`all` raise on Z3
expressions while `sum` works, and integer division and modulo disagree with
Python on negative operands. All of that is in the skill with the exact errors.

## Readiness

All ten required checks passed against image `dcp-eval/z3_python:v1`
(`sha256:cae05c65…`): satisfaction, changed_instances, enumeration,
minimization, maximization, isolation, malformed_output, empty_output,
timeout_cleanup, missing_image. Evidence copied here alongside the record at
`solvers/z3_python/readiness.json`.
