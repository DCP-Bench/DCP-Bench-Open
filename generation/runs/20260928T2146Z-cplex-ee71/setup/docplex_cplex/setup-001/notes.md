# Setup: docplex_cplex

IBM CPLEX 22.2 through DOcplex (`docplex.mp`), IBM's Python modelling API for
it, using the Community Edition in the cplex pip wheel.

## Outcome

Ready. All 19 checks passed on the first run.

## Files created

`solvers/docplex_cplex/` with `metadata.yaml`, `Dockerfile`, `run.py`,
`readiness_test.py`, `readiness.json`, `readiness/` and the skill bundle
`skills/docplex/`. Plus `tests/fixtures/model_docplex.py` with its registration
in `tests/test_solvers.py`, and one entry in the README's list of integrations.

## Versions

- base `python:3.12.11-slim-bookworm` by digest
- `cplex` 22.2.0.1 (the engine reports 22.2.0.0), `docplex` 2.32.264; pip also
  pulls in `six` 1.17.0. No NumPy.
- image build logs: `build-1.log`, `build-2.log`

## Licence

The cplex wheel is the Community Edition and needs no licence file or network.
Measured in the image (`probes/probe.py`): at most 1000 variables and 1000
constraints, indicator constraints included; past that, `solve()` raises
`DOcplexLimitsExceeded` with CPLEX code 1016. The runner reports it as
`unsupported`, and the `size_limit` check covers it.

The unrestricted CPLEX of the IBM Academic Initiative is installed from IBM's
installer rather than from pip. Whether it runs without network access was not
checked. It is not used here because the installer cannot be committed, so an
image built from it could not be rebuilt from this repository.

## Problems found, and the fix

- **CPLEX's default relative gap (1e-4) ends a solve with status 102, "integer
  optimal, tolerance", for a solution that is not optimal.** Measured on the
  same 40-item knapsack as the gurobipy integration: 12168379 with the default,
  12168772 (status 101) with the gap at 0. The runner sets the gap to 0; the
  `proven_optimum` check fails if it stops doing so.
- **The library prints some errors on standard output** ("Error: Model has
  non-convex quadratic constraint"), which would corrupt the JSONL protocol.
  The runner keeps a duplicate of fd 1 for the protocol and points fd 1 at
  stderr; `library_stdout` checks a submission that writes to fd 1 itself.
- **Integer variables come back within 1e-5 of an integer.** The runner rounds
  integer variables and evaluates declared linear expressions over the rounded
  values.

## Capabilities and limits

Satisfaction, minimisation, maximisation and enumeration of optimal solutions,
by the same pin-and-no-good scheme as the gurobipy integration, with docplex
indicators for general integers (`unbounded_enumeration`). One objective. No
products of variables: CPLEX refuses them as non-convex unless its
optimality target is changed, which the runner does not do.

## Checks

`satisfaction`, `changed_instances`, `enumeration`, `exhausted_enumeration`,
`unbounded_enumeration`, `minimization`, `maximization`, `optimal_enumeration`,
`proven_optimum`, `expression_output`, `library_stdout`, `isolation`,
`malformed_output`, `empty_output`, `fractional_output`, `unproven_optimum`,
`size_limit`, `timeout_cleanup`, `missing_image`.

Every encoding in the modelling skill was brute-forced over small domains in
the image, and the size of each docplex helper measured (`probes/snippets.py`):
all passed. The probes run in the image with their folder mounted at `/probe`.
