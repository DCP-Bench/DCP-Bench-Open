---
name: chuffed-cpp
description: Write or repair a C++ model for the native Chuffed 0.14.0 solver (lazy clause generation) in the DCP-Bench container runner. Use when a submission for the chuffed_cpp solver must define Build(instance, outputs), post constraints on Chuffed IntVar/BoolView objects, and compile against dcp.h.
compatibility: Needs the repository evaluator, Docker, and the image dcp-eval/chuffed_cpp. Chuffed 0.14.0, C++17, nlohmann/json 3.11.2.
---

# Chuffed (native C++ API) models for DCP-Bench

Write one `.cpp` file that includes `dcp.h`, defines the function below and
nothing else. Do not define `main`.

```cpp
#include "dcp.h"
void Build(const json& instance, json& outputs);
```

`dcp.h` pulls in the Chuffed headers (`primitives.h`, `globals.h`, `modelling.h`,
`int-var.h`, `bool-view.h`, `branching.h`, `engine.h`, `vec.h`) and defines
`using nlohmann::json;`. Chuffed's global solver state is the model: every
call such as `createVars`, `int_linear` or `all_different` posts straight into
it. There is no model object to pass around.

Read the API in [references/api-cheatsheet.md](references/api-cheatsheet.md)
(one line per call, constraint tables, recipes) and complete, tested models in
[references/examples.md](references/examples.md). Sources are listed in
[sources.md](sources.md).

## Submission contract

- Read every instance quantity from `instance` (`instance.at("n")`,
  `instance.at("weights").get<std::vector<int>>()`). The same file is run on
  several instances, so do not hardcode data. A constant that belongs to the
  problem and not to the instance may be written in the code with a comment
  saying so.
- `outputs` is a JSON object whose keys are exactly the declared output names.
  Its leaves are the integers returned by `dcp::out(IntVar*)`, not values.
  Arrays are JSON arrays of those integers, nested for matrices:
  `outputs = {{"x", arr}, {"total", dcp::out(total)}};`.
  `dcp::out` registers one variable and may be called again for the same
  variable.
- Only `IntVar*` can be an output. A Boolean output is an IntVar in 0..1 linked
  with `bool2int(boolView, intVar)`, then exported. A `BoolView` cannot be
  passed to `dcp::out`.
- An output variable must hold exactly the value the reference reports: create
  an auxiliary IntVar and constrain it equal to the expression, for sums,
  constants or any value that is not already a variable.
- An optimization problem calls `optimize(obj, OPT_MIN)` or
  `optimize(obj, OPT_MAX)` once, with a single IntVar `obj` and the same
  direction as the problem. Integer objectives only. If the objective is a
  declared output, export `obj` itself. Never bound the objective by a value you
  know from elsewhere.
- Log only to stderr (`std::cerr`). The driver redirects stdout, but do not rely
  on it. Do not call `engine.solve`, `parseOptions` or any solver entry point.
- Throwing an exception (`instance.at` on a missing field) is reported as an
  `error` status.

## Comments are part of the submission

Open the file with one comment line stating what the problem is. Start every
group of constraints with a comment that says what the group means in the
words of the problem statement, for example `// every row must contain different
values` above the loop that posts `all_different` on each row, or `// the total
weight of the chosen items must not exceed the capacity`. Name variables with
the problem's vocabulary (`take`, `start`, `queens`), not the encoding's. Add a
sentence where a bound comes from (an instance field or a derivation) and where
an unusual encoding works around a Chuffed limitation. The comment says what the
constraint means, not which function is called. The repository's acceptance
rules (`skills/model-generator/references/acceptance.md`) require this.

## How the driver solves

The driver forks a process per phase, so Chuffed's globals are fresh each time
and `Build` runs once per phase.

- Satisfaction: it enumerates solutions, keeps those that are distinct on the
  declared outputs, and stops at the solution limit or when the search is
  exhausted. Variables that are not outputs are not compared, so two solutions
  that differ only in an auxiliary variable count once.
- Optimization: phase 1 proves the optimum and emits nothing until it is
  proven. If the proof does not finish in the time budget the result is
  `timeout` with no solution, even if good solutions were found. Phase 2 fixes
  the objective to the optimum and enumerates distinct outputs.
- After any `branch(...)` you declare, the driver appends a fallback that
  branches on all integer variables in creation order, then VSIDS on the
  remaining Booleans. Without your own `branch`, the search follows creation
  order over every auxiliary variable, which is often poor. Declare
  `branch(decisionVars, VAR_..., VAL_...)` on the main decision variables
  (the ones everything else is functionally determined from), in a sensible
  order. The branch call needs a named `vec<IntVar*>`.
- Solutions are checked against a CPMpy reference, so a variable that is free
  in your model but fixed in the reference only passes when every value it
  takes is acceptable. Constrain output variables fully.

## Workflow

1. `python -m generation.brief PROBLEM` prints declared output names and
   shapes, the objective direction, and every instance field with its shape.
2. Write `MODEL.cpp` following the contract above.
3. `python -m evaluation.check MODEL.cpp --problem PROBLEM --solver chuffed_cpp`
   (add `--instance-count 3 --solution-limit 5` for a stronger test). The
   result is one JSON object with `accepted`, `reason` and `detail`.
4. Read `reason` and `detail`. `compilation_error`: the compiler message is in
   `detail`; fix the first error only and rerun. `invalid_output`: an output
   leaf is not a registered index, a name is missing, or a value is not an
   integer. `invalid_solution`: the model accepts something the reference
   rejects, so a constraint is missing or too weak. `suboptimal_solution` or
   `no_solution`: wrong objective direction or an overconstrained model.
   `execution_timeout`: the search is too weak, so add a `branch`, a tighter
   domain, or a global constraint. `execution_error`: an exception from
   `Build` or a crash.
5. Repeat a bounded number of times; do not edit the reference or evaluator.

## Compile pitfalls

Chuffed's API is raw C++ with no expression objects. Most compile errors come
from these.

- Every constraint takes `vec<...>&`, a non-const lvalue reference. There is no
  `std::vector` overload, no initializer list, and a temporary does not bind.
  Declare `vec<IntVar*> t; t.push(a); t.push(b);` first, then call.
  `vec<int>` for coefficients works the same way.
- There are no expressions. `x + y`, `a * b` and `2 * x` do not exist for
  IntVars. Create an IntVar for every intermediate result and post
  `int_linear`, `int_times`, `int_plus`, and the like. The result variable
  needs a domain wide enough for every value, or the problem is infeasible.
- Constants: most calls have an `int c` overload; use it. Where only IntVar* is
  accepted, use `getConstant(k)`.
- `~b` needs a named `BoolView` lvalue. Write `BoolView nb = ~b;` and not
  `~newBoolVar()` or `~v[i]` on a temporary.
- `vec<IntVar*>` and `vec<BoolView>` do not convert to each other. Use the
  `bool_*` and `array_bool_*` calls for BoolViews, and `bool2int` to cross over.
- Element: `array_int_element(index, table, result, offset)` reads
  `table[index - offset]`. The default offset is 0, so a 1-based index needs
  `offset = 1`. Keep the index domain inside the table. There is no 2-D element:
  flatten the table row-major and compute `idx = cols * r + c` with
  `int_linear`.
- Keep every domain inside +-500,000,000 and every sum inside `int`. Lower and
  upper bounds are required on `createVars`/`newIntVar`; give tight ones.
- Pass `true` as the last argument of `createVars` (eager) for small domains
  that you reify or read with `getLit`.
- `createVars(vec, n, lo, hi)` appends to an empty vec; call it once per vec.
  `flatten` and `transpose` also need an empty output vec.
- Reified and half-reified forms exist only for linear and binary relations.
  Encode anything else with `BoolView`s and `array_bool_and/or`.
- Argument order of `int_rel_reif`: `(x, rel, y, r, offset)` for variables and
  `(x, rel, c, r)` for a constant. The BoolView comes before the offset.

## Style

- Write a clear sequence: declarations,
  groups of constraints each with its comment, branching, optimize, outputs.
- Prefer a global (`all_different`, `table`, `circuit`, `cumulative`) over a
  decomposition, and `bool_linear`/`int_linear` over hand-built sums.
- Check the result at least on the example instance and on a second instance
  with different data before keeping the model.
