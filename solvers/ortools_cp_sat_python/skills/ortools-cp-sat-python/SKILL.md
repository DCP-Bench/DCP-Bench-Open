---
name: ortools-cp-sat-python
description: Generate or repair instance-agnostic OR-Tools CP-SAT Python submissions for DCP-Bench evaluation.
---

Write one Python entrypoint defining `build(instance) -> (model, outputs)`.
Read parameter values from the supplied JSON object. Return a `cp_model.CpModel` and a dictionary mapping exactly the declared output names to integer/Boolean variables, integer linear expressions, constants, or nested arrays of these.
Do not solve or print solutions. The runner owns `CpSolver`, time limits, objective fixing, output serialization, and blocking previously returned output assignments.
Use OR-Tools 9.15.6755 and integer objectives; floating-point objectives are unsupported.
Do not block internal auxiliary assignments yourself: enumeration is over declared outputs.

A working example is `tests/fixtures/model_cp_sat.py`; the evaluator is documented in `evaluation/README.md`.
Check with `python -m evaluation.check MODEL.py --problem PROBLEM --solver ortools_cp_sat_python`.
Repair the submission from diagnostics without changing the evaluator or reference.
