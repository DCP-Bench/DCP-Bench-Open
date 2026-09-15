---
name: minizinc-gecode
description: Generate or repair instance-agnostic MiniZinc models for the DCP-Bench Gecode integration.
---

Write one `.mzn` entrypoint. Declare instance parameters with names matching the supplied JSON fields; do not assign example values. The runner supplies JSON through the MiniZinc data interface, including nested arrays.
Include an `output` item producing one JSON object with exactly the problem's declared output names and their values. Auxiliary MiniZinc variables must not create extra output fields. Use valid JSON Booleans or 0/1 for Boolean outputs.
For satisfaction use `solve satisfy;`. For optimization expose an integer variable named `objective`, equate it to the objective expression, and put either `solve minimize objective;` or `solve maximize objective;` alone on a line, without solve annotations or trailing comments. This convention lets the runner fix the optimum and enumerate optimal outputs in a second satisfaction solve.
The integration uses MiniZinc 2.9.3 and Gecode. Data with native sets/enums or other problem-specific encodings requires a separately implemented integration/converter; do not quietly reinterpret JSON fields.

A working example is `tests/fixtures/model.mzn`; the evaluator is documented in `evaluation/README.md`.
Check with `python -m evaluation.check MODEL.mzn --problem PROBLEM --solver minizinc_gecode`.
Repair the candidate, not the reference or acceptance rules.

## When Gecode runs out of time

`execution_timeout` on a larger instance is usually propagation, not encoding.
Before reaching for a different model, add the constraints every solution
already satisfies but that Gecode cannot derive — a total that follows from an
`all_different` over a known set, a bound implied elsewhere in the model. They
remove no solution, and on this benchmark they are often the difference between
finishing an instance and not: `csplib_049_number_partitioning` times out on
n = 20 without the two implied half-totals and is accepted with them.

Search annotations are not available here — the solve item must stay
`solve satisfy;` or an unannotated `solve minimize objective;` — so implied
constraints and a tighter domain are the tools you have.

Never add a constraint that removes solutions to buy speed. Symmetry breaking a
reference keeps commented out is not part of the contract, and a model that
narrows the problem can pass the evaluator while being wrong.

## A one-sided bound can cost you the variable

MiniZinc 2.9.3 can flatten a model in which an auxiliary variable is bounded
from one side so that the variable doing the bounding **disappears from another
constraint it belongs to**. Several references have this shape — a flag that is
only upper-bounded by what enables it, as in `csplib_056_sonet` or
`cell_tower`'s `covered[j] <= sum_i delta[i][j] * build_tower[i]`.

Translated literally, alongside `sum_i cost[i] * build_tower[i] <= budget`,
MiniZinc compiled that pair to

```
constraint int_lin_le([3,4],[X_6,X_9],4);   % X_6 = build_tower[1], X_9 = covered[2]
```

leaving `build_tower[2]` in no constraint at all. It then takes either value,
and the runner reports a solution that spends more than the budget. MiniZinc's
own output item evaluates the budget constraint to `false` on that solution, and
Chuffed reproduces it, so this is the flattening rather than the solver.

**State the relationship as an equivalence** — `covered[j] <-> exists(i)(...)` —
whenever the reference's one-sided bound is tight at every solution you may
report, which for an optimisation is every optimum. That flattens soundly.

How it shows up: `invalid_solution` from the evaluator on a model you cannot
fault by reading. To confirm it rather than guess, compile with
`minizinc --solver gecode -c model.mzn` and look for a declared variable that
appears in no constraint, or add the suspect constraint to the `output` item and
watch it print `false` on a returned solution.
