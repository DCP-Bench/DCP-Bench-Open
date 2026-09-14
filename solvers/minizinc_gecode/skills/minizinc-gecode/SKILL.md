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
