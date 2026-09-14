# Setup: `pulp_cbc`

PuLP with the CBC binary it ships — mixed-integer linear programming, the one
modelling paradigm this repository had no integration for. The seven existing
ones are five CP, one SMT and one ASP; none of them can be used to ask how a
problem in this dataset looks when it has to be linear.

## Files created

| Path | What it is |
| --- | --- |
| `solvers/pulp_cbc/metadata.yaml` | integration metadata, same key set as the others |
| `solvers/pulp_cbc/run.py` | image entrypoint: solving, optimality, enumeration, protocol |
| `solvers/pulp_cbc/Dockerfile` | `python:3.12.11-slim-bookworm` plus one pinned wheel |
| `solvers/pulp_cbc/readiness_test.py` | the thirteen checks below, driven through the real evaluator |
| `solvers/pulp_cbc/skills/pulp-cbc/` | modelling skill, its sources and its behavioural cases |

Nothing outside `solvers/pulp_cbc/` was touched: `runner/runtime.py` and
`runner/requirements.txt` are shared with the certified images and stayed as
they were.

## Versions and sources

- Base image `python:3.12.11-slim-bookworm`, digest
  `sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7`,
  the same base the other Python integrations use.
- `pulp==3.3.2`, which bundles the CBC executable it calls, so the image needs
  no second install and no network at run time.
- Built image `dcp-eval/pulp_cbc:v1`, id
  `sha256:8a21cd8ade8fdff5cd1536d2f69bc914941930aaa24c9dd7eb9bc8957527bca9`.
- Documentation used is listed in `solvers/pulp_cbc/skills/pulp-cbc/sources.md`;
  every API claim in the skill was additionally run inside this image.

## The design decisions

**Instance handling** follows the pattern the Python integrations already use:
the submission reads the instance dict itself. PuLP is an API you call, so
neither generating source nor binding parameters outside the model was needed.

**Objective detection needs no convention.** PuLP leaves `problem.objective` as
`None` until a bare expression is added, and carries the direction in the
problem's `sense`, so `build(instance)` returns `(problem, outputs)` and nothing
else — a satisfaction model simply adds no objective.

**Two properties of CBC shaped `run.py`:**

1. *CBC reports `status == Optimal` even when it stopped on the time limit.*
   Only `sol_status` separates a proven optimum from a feasible point. A runner
   reading `status` would let an unproven optimum pass as a result, so every
   solve here is judged on `sol_status`. The `unproven_optimum` readiness check
   exists to fail if that guard is ever removed: a 60-item knapsack under a 5 s
   budget must come back `execution_timeout`, not accepted.
2. *A MIP solver returns one solution, not a stream.* Enumeration pins the
   objective to the proven optimum and adds a no-good cut over the integer
   variables the declared outputs are built from: for each variable at value
   `a`, an indicator for `v <= a - 1` and one for `v >= a + 1`, at least one of
   them on. That needs those variables to be integral and bounded, and the
   runner says `unsupported` with the offending variable named when they are
   not, rather than silently returning fewer solutions.

Declared outputs are rounded to integers within 1e-6 and refused otherwise,
because CBC returns floats and a fractional declared output is a modelling
error, not solver noise.

## Readiness

`python -m generation.readiness check --solver pulp_cbc` ran
`solvers/pulp_cbc/readiness_test.py` against the built image; the record is
`solvers/pulp_cbc/readiness.json` and the evidence is in
`solvers/pulp_cbc/readiness/`. All thirteen checks passed:

`satisfaction`, `changed_instances`, `enumeration`, `exhausted_enumeration`,
`minimization`, `maximization`, `isolation`, `malformed_output`, `empty_output`,
`fractional_output`, `unproven_optimum`, `timeout_cleanup`, `missing_image`.

The last three beyond the required set are the ones specific to this
integration: a fractional declared output must be refused, an unproven optimum
must not look like success, and an exhausted enumeration must report `complete`
rather than a shortfall.

## Known limits

- No compilation step, so `compilation: true` is not declared and the
  `compilation_error` check does not apply.
- Enumeration needs bounded integer declared outputs; with a continuous or
  unbounded one the runner reports `unsupported` for a solution limit above one.
  The modelling skill tells modellers to declare bounds, which they should
  anyway.
- CBC is a branch-and-bound MIP solver: problems whose references are written
  with all-different or disjunctions need big-M encodings, and those are the
  ones where it runs out of the execution budget first.
- Only one submission file is staged, so a model cannot ship a helper module.
