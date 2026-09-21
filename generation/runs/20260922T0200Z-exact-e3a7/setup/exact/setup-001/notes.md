# Setup: exact

Exact 2.2.1, a pseudo-Boolean solver, through its Python bindings.

## Outcome

Ready. All ten required checks passed on the first run.

## Files created

`solvers/exact/` with `metadata.yaml`, `Dockerfile`, `run.py`, `dcp_pb.py`,
`readiness_test.py`, `readiness.json` and the skill bundle. Plus
`tests/fixtures/model_exact.py` with its registration, and one line in the README.

## Versions

- base `python:3.12.11-slim-bookworm` by digest
- `exact` 2.2.1; no other solver dependency
- image identity at readiness: `sha256:615af09c6bff39570f059aca39a04f7920524f9edafcef228a0f0353566ab4f0`

## Why this layer is thin

Exact takes integer variables with bounds and linear constraints with integer
coefficients directly, and its objective is a linear expression. So unlike the
SAT and MaxSAT integrations in this repository, nothing has to be one-hot
encoded up front and no auxiliary variable is needed to carry the objective.
What the layer adds is channelling: 0/1 indicators tied to a variable, built on
first use, which is what all-different, counting and element are expressed
through.

## Problems hit, and the fix

- **`toOptimum` answers `"SAT"` when it proved the optimum**; there is no
  `"OPTIMAL"` state. The first runner compared against the wrong string and
  reported every proven optimum as a timeout.
- **`hasSolution()` is true even after `"TIMEOUT"`.** Reading the solution
  without reading the state would pass off an unproven answer as optimal, which
  is the one failure this benchmark exists to catch.
- **Maximisation optima come back negated**, because Exact minimises
  internally. Pinning the objective for enumeration has to flip the sign, or
  enumeration searches at the wrong value.
- `inspect.signature` raises `ValueError` on the pybind11 bindings; the method
  `__doc__` carries the real signatures.

## Capabilities and limits

Satisfaction, minimisation, maximisation and enumeration of optimal solutions.
Exact bounds its own search, so the runner hands it the remaining budget and
needs neither a timer thread nor a child process. No multiplication of two
variables, no division, no modulo through this layer.
