# Sources for `z3-python`

Tested with z3-solver 5.1.0.0 (package version; `z3.get_version_string()` prints the Z3 core version 5.1.0), Python 3.12.11, Linux (Docker image `dcp-eval/z3_python:v1`). The install is unpinned; PyPI's latest was 5.3.0.0 at the time of this round and was not re-tested.

Existing skills: not searched in this refactor; the skill was refactored from the DCP-Bench integration skill.

- <https://z3prover.github.io/api/html/namespacez3py.html> — Z3 Python API reference
- <https://z3prover.github.io/api/html/classz3py_1_1_solver.html> and <https://z3prover.github.io/api/html/classz3py_1_1_optimize.html> — `Solver` and `Optimize` methods
- <https://microsoft.github.io/z3guide/docs/logic/intro/> — Z3 guide, logic introduction
- <https://microsoft.github.io/z3guide/docs/optimization/intro/> — Z3 guide, optimisation
- <https://microsoft.github.io/z3guide/docs/theories/Arithmetic/> — Z3 guide, arithmetic theory
- <https://pypi.org/project/z3-solver/> — package name, MIT licence
- <https://github.com/Z3Prover/z3> — Z3 source and `examples/python`

Verified by running (inside the image, Z3 5.1.0):
- Names: `Distinct`, `Sum`, `Product`, `Abs`, `If`, `PbEq`, `PbLe`, `PbGe`, `AtMost`, `AtLeast`, `Select`, `Store`, `Array`, `IntVector`, `BoolVector` and `Optimize` exist; `Max`, `Min`, `Element`, `AllDifferent`, `Table`, `Circuit`, `Cumulative` and `NoOverlap` do not (`AttributeError`).
- Python `max`, `min`, `any` and `all` on Z3 expressions raise `Z3Exception: Symbolic expressions cannot be cast to concrete Boolean values`; Python `sum` returns `0 + x + y`; `z3.Sum` and `z3.Product` return Z3 expressions.
- `bool(x == 3)` for a symbolic `x` is `False`; for two numerals it is `True`.
- Integer division and modulo: Z3 gives `7 / -2 = -3`, `7 % -2 = 1`, `-7 / -2 = 4`, `-7 % -2 = 1`; Python gives `-4`, `-1`, `3`, `-1`. Both agree on `7 / 2`, `-7 / 2`, `-7 % 2`.
- `Optimize.lower(h)` and `upper(h)` agree at the optimum; an unbounded minimise gives `-1*oo` for both.
- `model()` after `unsat` raises `Z3Exception: model is not available`; `reason_unknown()` gives `timeout` for a nonlinear cube-sum under `set("timeout", 5000)`.
- `model.eval(..., model_completion=True)` gives defaults for unconstrained variables; a `Real` value of 1/3 comes back as `1/3`.
- Blocking-clause enumeration: 3 of 3 for exactly-one over three Booleans; `Optimize` plus pinned objective gives 3 optimal points for `c0 + c1` maximised.
- All examples in `assets/` run and print their expected lines inside the image.
- Distinct-value minimisation: one `used` flag per value with `Optimize.minimize` gives 3 colours on Petersen and 4 on k4-tail, with `lower == upper`; the colour values come back non-contiguous (e.g. 9, 5, 4), which is why the flag form is used.
- `Optimize.upper(h)` and `lower(h)` return `IntNumRef` for finite optima (`z3.is_int_value` is True); for an unbounded objective `as_long()` raises `AttributeError` (`ArithRef`).
- Big-M no-overlap on the 6x6 job-shop (ft06, 36 tasks): `Implies` form, linear form with `M = sum of durations`, and fixed `M = 10**6` each reached makespan 55 in 0.3 to 0.4 s; the pairwise `z3.Or` form reached 55 in about 0.5 s. The add-solver toy README reports naive big-M timing out on ft06; this could not be reproduced with these variants, so the skill does not repeat that claim.
- Program interface: a model reading `n_nodes` and `edges` by name from a file that also carries `name` and `note` keys runs and prints one JSON line (exit 0).

Independent toy test (add-solver, fresh agent, skill only; models in `<workspace>/round-1/models/`, results in `round-1/results.txt`). Round 1 ran on the previous version of this skill and passed 18/18 at first attempt, with no repairs. The gaps it reported (program interface, distinct-value minimisation, big-M and pairwise scheduling, optimum reading, version mismatch, JSON output) were closed in this revision, and the examples and evals now cover them. Re-test this revision with a fresh agent before shipping:

| Problem | Instance | Result |
|---|---|---|
| cryptarithm | ab-ab-aaa | PASS infeasibility reported |
| cryptarithm | send-more-money | PASS feasible solution |
| cryptarithm | two-two-four | PASS feasible solution |
| graph-colouring | cycle6 | PASS optimal (2) |
| graph-colouring | k4-tail | PASS optimal (4) |
| graph-colouring | petersen | PASS optimal (3) |
| jobshop | ft06 | PASS optimal (55) |
| jobshop | small | PASS optimal (11) |
| knapsack | p01 | PASS optimal (309) |
| knapsack | small | PASS optimal (15) |
| knapsack-all-optimal | fourteen | PASS all 9 optimal solutions |
| knapsack-all-optimal | ties | PASS all 5 optimal solutions |
| knapsack-all-optimal | unique | PASS all 1 optimal solutions |
| n-queens | n3 | PASS infeasibility reported |
| n-queens | n4 | PASS feasible solution |
| n-queens | n8 | PASS feasible solution |
| n-queens-all | n6 | PASS all 4 solutions |
| n-queens-all | n8 | PASS all 92 solutions |

Independent toy test result: **18/18 passed** (runner exit code 0, z3 5.1.0, first attempt).

Refactored from the DCP-Bench integration skill; examples verified inside the dcp-eval/z3_python:v1 image.
