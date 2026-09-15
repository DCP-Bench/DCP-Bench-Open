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
