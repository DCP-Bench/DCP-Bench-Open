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

## Where a compile costs you an attempt

Compilation happens before search, so a type error spends a whole model attempt
without ever testing the model. These are the signatures that catch people out
in 9.15.

- **`AddElement` takes a span of `LinearExpr`, not of `IntVar`.** The overloads
  are `AddElement(LinearExpr index, absl::Span<const LinearExpr> exprs,
  LinearExpr target)` and a second one taking `absl::Span<const int64_t>`
  constants. A `std::vector<IntVar>` — which is what you have on hand — converts
  to neither, and the error is a wall of candidate listings. Convert once and
  reuse:

  ```cpp
  const std::vector<LinearExpr> exprs(vars.begin(), vars.end());
  model.AddElement(index, exprs, target);
  ```

  The same conversion is what `AddAllDifferent` and `AddMaxEquality` need when
  the arguments are expressions such as `queens[i] - i` rather than plain
  variables.
- **Index a 2-D table by flattening it.** With two decision variables choosing a
  row and a column, build the flat `std::vector<LinearExpr>` once and compute
  the position with a linear constraint: `model.AddEquality(cell, width *
  row_var + column_var)`, then one `AddElement` on `cell`.
- **`BoolVar` is a valid output leaf.** `BoolVar::index()` is nonnegative for a
  positive literal, so a Boolean output can be a `BoolVar` directly; there is no
  need to mirror it into an `IntVar` with domain `0..1`. Booleans also enter
  `LinearExpr` arithmetic directly, so `total += weight * take[i]` works.

## Reifying and the constraints that need it

`OnlyEnforceIf` reifies, but only half of it: post **both** directions or the
indicator is free to take the value that suits the search.

```cpp
BoolVar hit = model.NewBoolVar();
model.AddEquality(x[i], value).OnlyEnforceIf(hit);
model.AddNotEqual(x[i], value).OnlyEnforceIf(hit.Not());
```

That pattern is how you count occurrences, express `sum(x == v) == k`, and
translate a CPMpy disjunction: reify each disjunct, then `AddBoolOr` over the
indicators.

`Domain::FromValues({a, b})` states a domain with a hole, which is how
`(x == 8) | (x == 9)` and a `+/-1` variable are written, the latter via
`model.NewIntVar(Domain::FromValues({-1, 1}))`.

## Constraints verified in this image

`AddAllDifferent`, `AddElement`, `AddModuloEquality`,
`AddMultiplicationEquality` (chain it two factors at a time for a longer
product), `AddAbsEquality`, `AddMinEquality`, `AddMaxEquality`,
`AddLinearConstraint` with a `Domain`, `AddBoolOr`, `AddBoolAnd`,
`AddImplication`, `AddNoOverlap2D` with `NewFixedSizeIntervalVar`, and
`AddAutomaton` — whose `AutomatonConstraint::AddTransition(tail, head, label)`
is the way to express a regular-language constraint such as a nonogram clue.
