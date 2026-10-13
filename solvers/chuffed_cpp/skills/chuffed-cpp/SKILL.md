---
name: chuffed-cpp
description: Write, build and run C++ models for the Chuffed 0.14.0 lazy clause generation CP solver through its native API (standalone programs linked against an installed Chuffed). Also covers DCP-Bench Open submissions for the chuffed_cpp integration (Build(instance, outputs) against dcp.h).
compatibility: Chuffed 0.14.0, C++17, CMake 3.18+. DCP-Bench use needs the repository and the Docker image dcp-eval/chuffed_cpp.
---

# Chuffed 0.14.0 C++ models

Chuffed is a CP solver with lazy clause generation. Its C++ API is raw: global
solver state is the model, so `createVars`, `int_linear`, `all_different`, ...
post straight into it. Other files: [references/api-cheatsheet.md](references/api-cheatsheet.md)
(calls, tables, recipes), [references/examples.md](references/examples.md),
[sources.md](sources.md).

## Build and link

Chuffed installs a CMake package (prefix e.g. `/opt/chuffed`, set `CMAKE_PREFIX_PATH`).

```cmake
cmake_minimum_required(VERSION 3.18)
project(models LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
find_package(chuffed CONFIG REQUIRED)
find_package(Threads REQUIRED)
add_executable(queens queens.cpp)
target_include_directories(queens PRIVATE ${CHUFFED_INCLUDE_DIRS})
target_link_libraries(queens PRIVATE chuffed chuffed_fzn chuffed Threads::Threads)
```

`chuffed` is listed twice on purpose (static library cycle). Build Release:
`cmake -S . -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build`.

## Program shape

Complete tested programs: [standalone_queens.cpp](references/standalone_queens.cpp) (satisfaction,
n from argv), [standalone_knapsack.cpp](references/standalone_knapsack.cpp) (optimization).

- Headers: `<chuffed/{branching/branching,core/engine,core/options,globals/globals,primitives/primitives,support/vec,vars/int-var,vars/modelling}.h>`.
- Subclass `Problem`, post the model in the constructor, override `void print(std::ostream&)`.
- `main`: set options, then `engine.solve(new P(...))`.
- Options: fields of the global `so`: `so.nof_solutions` (default 1, 0 = all), `so.time_out = std::chrono::milliseconds(ms)`, `so.print_sol`, `so.vsids`. `parseOptions(argc, argv)` reads Chuffed's CLI flags and can exit on unknown flags; do not use it with your own arguments.
- Values: `x->getVal()` (IntVar), `b.getVal()` (BoolView, 0/1) only inside `print` or the callback, where all variables are fixed.
- `engine.setSolutionCallback(f)`, with `f` a `std::function<void(Problem*)>` (a lambda), runs per solution.
- After solve: `engine.status` is `RES_SAT` (stopped at limit, solutions may remain), `RES_UNK` (time out), `RES_GUN`/`RES_LUN` (search complete); `engine.solutions` counts solutions; `engine.best_sol` is the best objective value (optimization).
- To enumerate several solutions declare `output_vars(vec)` on the variables that tell solutions apart; without it search ends after the first.
- One solve per process: Chuffed globals cannot be reset. To solve twice, fork or restart.
- Chuffed calls `exit(0)` when posting a constraint fails at the root (infeasible model): no `print`, no status. Treat exit 0 with no output as unsatisfiable.
- Without any `branch(...)` call Chuffed reports an unfixed root "solution". Always declare branching on the decision variables.
- Log to stderr; Chuffed prints solutions and `==========` / `=====UNSATISFIABLE=====` to stdout.

## Modelling rules

- Comment each conceptual constraint block with one line taken from the problem statement (`// all rows must have different values`). Open the file with a line stating the problem. Name variables in the problem's vocabulary. Comment where a bound comes from and where an encoding works around a Chuffed limit.
- Order: variables, constraint blocks, branching, `optimize`, output.
- Prefer globals (`all_different`, `table`, `circuit`, `cumulative`) over decompositions and `int_linear`/`bool_linear` over hand-built sums.
- Tight domains from the data. One `optimize` call, one IntVar objective, integer only.
- Test on a second instance with different data.

## Compile and runtime pitfalls

- `vec` copies are shallow. `vec<IntVar*> a = b;` or pushing a local `vec` into a `vec<vec<>>` crashes with "double free or corruption" (signal 6). Build rows in place: `m.push(); m.last().push(x);` or `createVars(m.last(), ...)`. Never copy a constraint's argument vec.
- Constraints take `vec<...>&` (non-const lvalue). No `std::vector`, no initializer list, no temporary. Declare `vec<IntVar*> t; t.push(a); t.push(b);` first. Same for `vec<int>`.
- No expressions: `x + y`, `2 * x` do not exist. Make an IntVar per intermediate and post `int_linear`/`int_plus`/`int_times`. Its domain must hold every value or the model is infeasible.
- Constants: use the `int c` overload; where only `IntVar*` is accepted use `getConstant(k)`.
- `~b` needs a named `BoolView` lvalue: `BoolView nb = ~b;`.
- `vec<IntVar*>` and `vec<BoolView>` do not convert. Use `bool_*`/`array_bool_*` for BoolViews, `bool2int(b, intVar)` to cross over. `BoolView r = x;` from an `IntVar*` does not compile.
- `branch` takes a named flat `vec<IntVar*>`, not `vec<BoolView>` (branch on the 0/1 IntVars from `bool2int`) and not `vec<vec<>>` (`flatten` first).
- `array_int_element(index, table, result, offset)` reads `table[index - offset]`; default offset 0, so a 1-based index needs `offset = 1`. Keep the index domain inside the table. No 2-D element: flatten row-major, `idx = cols*r + c` via `int_linear`.
- Domains within +-500,000,000, sums within `int` (32-bit). A value that can exceed this (a 10-digit number) cannot be one variable: split it into digits or blocks if the output allows, else the problem is out of reach. Bounds are required on `createVars`/`newIntVar`.
- `newIntVar(lo, hi)` has no eager flag. Eager one: `IntVar* v; createVar(v, lo, hi, true);`. Pass `true` last to `createVars` for small domains you reify or read with `getLit`.
- `createVars(vec, n, lo, hi)`, `flatten`, `transpose` need an empty output vec; call once per vec.
- `int_mod` compiles and aborts at run time ("Not yet supported"). Encode `x = q*y + r`, `0 <= r < y` with `int_linear`.
- `lex` crashed (signal 11) on rows of eager 0/1 variables; avoid there.
- Reified and half-reified forms exist only for linear and binary relations; encode the rest with BoolViews and `array_bool_and/or`.
- `int_rel_reif(x, rel, y, r, offset)` with variables, `(x, rel, c, r)` with a constant: the BoolView precedes the offset.

## Hard instances

- Branch first on the structural decisions everything else follows from, then the rest. Try `VAR_ACTIVITY` or `VAR_SIZE_MIN` when `VAR_INORDER` stalls.
- Tighten domains from the data (a shipment is at most min(capacity, demand)).
- Add implied constraints that bound the objective (cost >= demand x cheapest unit cost via `minimum` cut one facility-location proof from 190 s to 36 s).
- Redundant implied constraints help less than a good `branch`.

## Using this skill in DCP-Bench Open

Applies only to the `chuffed_cpp` integration. Everything above still holds; this adds the submission contract.

Submission: one `.cpp` that has `#include "dcp.h"`, defines `void Build(const json& instance, json& outputs);` and no `main`. `dcp.h` includes the Chuffed headers and `using nlohmann::json;`. Do not call `engine.solve`, `parseOptions` or `output_vars`. Log to `std::cerr` only. Examples: [references/examples.md](references/examples.md) (DCP format).

- Read every instance quantity from `instance` (`instance.at("n")`, `instance.at("w").get<std::vector<int>>()`). The same file runs on several instances; no hardcoded data. A problem constant may be written in code with a comment.
- `outputs` is a JSON object with exactly the declared output names. Leaves are the integers returned by `dcp::out(IntVar*)`, nested arrays for matrices: `outputs = {{"x", arr}, {"total", dcp::out(total)}};`. `dcp::out` may be called twice on one variable.
- Only `IntVar*` can be an output. A Boolean output is a 0..1 IntVar linked by `bool2int(boolView, intVar)`. A `BoolView` cannot go to `dcp::out`.
- An output variable must hold exactly the value the reference reports: for sums, constants or other expressions create an IntVar constrained equal to it. Constrain outputs fully; a variable free in the model but fixed in the reference passes only if every value is acceptable.
- Optimization: `optimize(obj, OPT_MIN|OPT_MAX)` once, direction as in the problem. If the objective is an output, export `obj`. Never bound it by a value known from elsewhere.
- A thrown exception (`instance.at` on a missing field) is an `error` status.
- Comment rule above is required by `skills/model-generator/references/acceptance.md`.

How the driver solves: forks one process per phase (`Build` runs once per phase, globals fresh).
- Satisfaction: enumerates solutions distinct on the declared outputs, until the solution limit or exhaustion. Auxiliary variables are not compared.
- Optimization: phase 1 proves the optimum and emits nothing before; if the proof misses the time budget the result is `timeout` with no solution. Phase 2 fixes the objective to the optimum and enumerates distinct outputs.
- After your `branch(...)` calls the driver appends branching on all integer variables in creation order, then VSIDS on the Booleans. Without your own `branch` search follows creation order over auxiliaries, which is poor. Declare `branch` on the main decision variables.

Output conventions: on "Declared outputs cannot extend to a reference solution" the outputs break a convention in the description (1-based vs 0-based, fixed first element for rotation-invariant arrangements, a stated order). Re-read the output sentence and pin that convention. Add no ordering the description does not ask for.

Workflow:
1. `python -m generation.brief PROBLEM`: output names and shapes, objective direction, instance fields.
2. Write `MODEL.cpp`.
3. `python -m evaluation.check MODEL.cpp --problem PROBLEM --solver chuffed_cpp` (stronger: `--instance-count 3 --solution-limit 5`). Result JSON has `accepted`, `reason`, `detail`.
4. By `reason`: `compilation_error` fix the first error in `detail`; `invalid_output` a leaf is not a registered index, a name is missing or a value is not an integer; `invalid_solution` a constraint is missing or too weak; `suboptimal_solution`/`no_solution` wrong direction or overconstrained; `execution_timeout` weak search, add `branch`, tighter domains or a global; `execution_error` exception from `Build` or a crash.
5. Repeat a bounded number of times; do not edit the reference or evaluator.
