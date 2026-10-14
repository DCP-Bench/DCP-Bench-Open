# Setup: gurobipy_python

Gurobi Optimizer 13.0.3 through gurobipy, its Python API, under the size-limited
licence bundled in the pip wheel.

## Outcome

Ready. All 20 checks passed; the first full run failed only `matrix_output`,
because the matrix API needs SciPy (see below).

## Files created

`solvers/gurobipy_python/` with `metadata.yaml`, `Dockerfile`, `run.py`,
`readiness_test.py`, `readiness.json`, `readiness/` and the skill bundle
`skills/gurobipy/`. Plus `tests/fixtures/model_gurobipy.py` with its
registration in `tests/test_solvers.py`, and one entry in the README's list of
integrations.

## Versions

- base `python:3.12.11-slim-bookworm` by digest
- `gurobipy` 13.0.3, `numpy` 2.4.6, `scipy` 1.18.1
- bundled licence: size-limited, "non-production use only", expires 2027-11-29
  (`Model.LicenseExpiration` = 20271129). After that date the image stops
  solving; a newer gurobipy wheel carries a newer licence.
- image build logs: `build-1.log` to `build-4.log`

## Licence

The evaluator runs candidates with `--network=none`. Gurobi documents that an
Academic Named-User licence cannot be used in a container and that an Academic
WLS licence needs an internet connection while it runs, so neither can work
here without weakening isolation, which setup may not do. The licence in the
wheel needs neither a file nor a network. Its limits, measured in the image
(`probes/limit_probe.py`, `probes/api_probe.py`):

- 2000 variables;
- 2000 constraints, counting linear and general constraints together
  (500 `abs_` + 1499 linear solves, 500 + 1501 fails; same with indicators);
- 200 variables once any quadratic or nonlinear term is present (199 with one
  product solves, 201 fails; `addGenConstrNL`/`addGenConstrPow` fail at 300).

Exceeding a limit raises `GurobiError` 10010 at `optimize()`. The runner reports
it as `unsupported`, which the evaluator maps to `unsupported_capability`; the
`size_limit` readiness check covers it.

## Problems hit, and the fix

- **Gurobi's default `MIPGap` (1e-4 in the 13.0.3 wheel, although the online
  parameter page lists `-1`) reports OPTIMAL for a solution that is not
  optimal.** Measured on a 40-item strongly correlated knapsack: default gap
  gives 12168379 with bound 12169590 and status OPTIMAL; the optimum is
  12168772 (`probes/gap2.py`, `probes/knap_probe.py`, which runs the check's
  own model). The runner sets `MIPGap=0`; the `proven_optimum` check fails if
  it stops doing so.
- **The licence banner goes to standard output from the library.** It would
  corrupt the JSONL protocol. The runner keeps a duplicate of fd 1 for the
  protocol and points fd 1 at stderr; `library_stdout` checks a submission that
  writes to fd 1 itself and turns logging back on.
- **Integer variables come back within `IntFeasTol` (1e-5) of an integer.** The
  runner rounds integer variables and evaluates declared expressions over the
  rounded values; a continuous output must be within 1e-6 of an integer.
- **The matrix API needs NumPy and SciPy**, which the wheel does not pull in:
  `MVar.sum()` raised `ModuleNotFoundError: No module named 'scipy'`. Both are
  pinned in the Dockerfile; `matrix_output` covers an `MVar` output.

## Capabilities and limits

Satisfaction, minimisation, maximisation and enumeration of optimal solutions.
Enumeration pins the objective (within 0.5 when the objective is integral,
otherwise within 1e-6 relative), replaces it by zero, and adds a no-good over
the integer variables behind the declared outputs: one linear constraint over
binaries, two indicator constraints per general integer, so no bound is needed
(`unbounded_enumeration`). One objective only. The licence limits above apply
to every model, including the constraints enumeration adds.

## Checks

`satisfaction`, `changed_instances`, `enumeration`, `exhausted_enumeration`,
`unbounded_enumeration`, `minimization`, `maximization`, `optimal_enumeration`,
`proven_optimum`, `expression_output`, `matrix_output`, `library_stdout`,
`isolation`, `malformed_output`, `empty_output`, `fractional_output`,
`unproven_optimum` (a market-split instance with a 5 s limit), `size_limit`,
`timeout_cleanup`, `missing_image`.

Every encoding in the modelling skill was brute-forced over small domains in
the image (`probes/snippets.py`): all passed.

The probes run in the image with their folder mounted at `/probe`, e.g.
`docker run --rm --network=none -v "$PWD/probes:/probe:ro" --entrypoint python
dcp-eval/gurobipy_python:v1 /probe/limit_probe.py`. `knap_probe.py` also reads
`knap_model.py` and `knap.json`, which are `KNAPSACK_MODEL` and the
`KNAPSACK_DATA` values from `readiness_test.py`.
