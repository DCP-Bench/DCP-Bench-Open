---
name: ortools-cp-sat-cpp
description: Generate or repair C++ OR-Tools CP-SAT submissions using the DCP-Bench container runner.
---

Write one `.cpp` entrypoint implementing this function; do not define `main`:

```cpp
void Build(const nlohmann::json& instance,
           operations_research::sat::CpModelBuilder& model,
           nlohmann::json& outputs);
```

Read all instance-specific parameters from `instance`. Populate `model` and set `outputs` to a JSON object whose keys exactly match the problem's declared outputs. Output leaves are **nonnegative IntVar proto indices**, obtained with `.index()`, not solution values. Nested JSON arrays represent output arrays.
Use auxiliary IntVars with equality constraints to expose linear expressions, constants, or Boolean outputs as integer 0/1 values. Use integer objectives only.
The supplied driver defines `main`, solves, fixes the objective, enumerates distinct outputs, and serializes values. Do not call a solver yourself. Log only to stderr.
The image provides C++17, OR-Tools 9.15.6755, nlohmann/json, and CMake. Compilation happens inside the container and has a separate time budget.

A working example is `tests/fixtures/model.cpp`; the evaluator is documented in `evaluation/README.md`.
Check with `python -m evaluation.check MODEL.cpp --problem PROBLEM --solver ortools_cp_sat_cpp`.
Repair candidate code from diagnostics without modifying the reference or evaluator.
