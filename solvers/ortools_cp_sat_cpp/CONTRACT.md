# ortools_cp_sat_cpp: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how OR-Tools
CP-SAT in C++ expresses it. Runner: [run.py](run.py), which calls `main("cpp")` in
[runner/runtime.py](../../runner/runtime.py) (`cpp_solver`). That compiles the submission
together with the driver [cpp/driver.cpp](cpp/driver.cpp) using
[cpp/CMakeLists.txt](cpp/CMakeLists.txt), then runs the binary, which owns `main`,
solving, enumeration and printing.

## Submission file

One C++17 source file, `model.cpp`, compiled as a second translation unit next to
`driver.cpp`. It includes what it uses itself (`<nlohmann/json.hpp>`,
`"ortools/sat/cp_model.h"`, the standard library); it must not define `main`.

## Entrypoint

```cpp
void Build(const nlohmann::json& instance,
           operations_research::sat::CpModelBuilder& model,
           nlohmann::json& outputs);
```

A free function in the global namespace with exactly this signature (the driver
declares it with `using nlohmann::json` and `using namespace
operations_research::sat`). The driver calls it once, then solves `model` itself.

## Instance

`instance` is the request's `instance` object as an `nlohmann::json`, 0-based. Read with
`instance.at("n")` (converts implicitly to `int`, `int64_t`, `std::vector<int>`,
`std::vector<std::vector<int>>`, `std::string` ...) or `.get<T>()`. JSON Booleans stay
JSON Booleans: read them with `.get<bool>()`, as the fixture does. Ragged arrays are
ordinary nested arrays (`instance.at("rows")[i].size()`). A thrown exception becomes
status `error` with its message as detail.

## Outputs

Set `outputs` to a non-empty JSON **object** keyed by the declared output names, whose
leaves are **CP-SAT proto indices** of variables, `var.index()`, nested in JSON arrays to
the declared shape:

```cpp
json grid = json::array();
for (auto& row : x) { json r = json::array(); for (auto& v : row) r.push_back(v.index()); grid.push_back(r); }
outputs = {{"grid", grid}, {"total", total.index()}};
```

The driver replaces each index with `response.solution(index)`, so every value is
reported as an integer; a `BoolVar` (positive literal) reports `0`/`1`. A leaf that is
not an integer, or an index outside the model, is an `error`. An expression or a
constant has to be an `IntVar` first (`model.NewIntVar(...)` plus `AddEquality`, or
`model.NewConstant(k)`).

## Objective

`model.Minimize(expr)` or `model.Maximize(expr)` on the builder, with an integer
`LinearExpr`. A floating-point objective is refused (`unsupported`).

## Solving

- The driver solves with `SolveWithParameters` and these parameters, which the model
  cannot change: `num_search_workers = 1`, `keep_all_feasible_solutions_in_presolve =
  true` (CP-SAT 9.11 to 9.15 dual presolve reductions can drop the optimum), and
  `max_time_in_seconds` set to what is left of the budget. Presolve is otherwise on, with
  CP-SAT's defaults.
- With an objective, only `OPTIMAL` is a result; without one, `OPTIMAL` or `FEASIBLE`.
  `INFEASIBLE` is `unsat` before any solution and `complete` after one; `MODEL_INVALID`
  is `error`; anything else (`UNKNOWN`, or `FEASIBLE` with an objective) is `timeout`.
- After a solution the driver re-solves: for optimisation it clears the objective and
  adds `objective == optimum` once, and after every solution it adds
  `AddForbiddenAssignments` over the distinct output variables with their reported
  values. Exhaustion is the re-solve returning `INFEASIBLE`.
- The budget is `execution_timeout`: the driver's clock starts after `Build` returns and
  each re-solve gets what is left; the runner kills the binary at `execution_timeout`
  counted from its start, `Build` included, and reports `timeout`. A nonzero exit is
  `error`.

## Compilation

Yes. `cpp_solver` copies the file to `/tmp/model.cpp` and runs `cmake -S /opt/cpp -B
/tmp/build -DCMAKE_BUILD_TYPE=Release` then `cmake --build /tmp/build -j1`, linking
`ortools::ortools` and `nlohmann_json::nlohmann_json`. Both steps share one budget,
`compilation_timeout` (default 120 s); running out or a compiler error is
`compilation_error`, with the compiler output on stderr. The binary then gets
`execution_timeout`, which includes `Build`.

## Environment

Image `dcp-eval/ortools_cp_sat_cpp:v1`: g++ 12.2 (Debian bookworm), CMake 3.25.1,
OR-Tools 9.15.6755 (the official C++ archive, with its bundled Abseil and protobuf),
nlohmann/json 3.11.2 as the JSON library (`/usr/include/nlohmann/json.hpp`), Python
3.12.11 for the runner. OR-Tools is unpacked at `/opt/ortools` (headers in
`include`, libraries in `lib`, CLI tools such as `solve` and `fzn-cp-sat` in `bin`, not
on `PATH`); the CMake project the runner builds is `/opt/cpp`. The image sets
`CMAKE_PREFIX_PATH=/opt/ortools` and `LD_LIBRARY_PATH=/opt/ortools/lib`; configuring
without `CMAKE_PREFIX_PATH` fails in `ortoolsConfig.cmake` with "Could NOT find ZLIB".
The evaluator runs the container with no network, a read-only root file system, user
65534, `HOME=/tmp`, a 512 MiB writable `/tmp` and `/input` read-only. For an ad hoc
build, override the entrypoint and repeat the runner's steps: `docker run --rm --network
none -v $PWD/model.cpp:/tmp/model.cpp:ro --entrypoint sh dcp-eval/ortools_cp_sat_cpp:v1
-c 'cmake -S /opt/cpp -B /tmp/b -DCMAKE_BUILD_TYPE=Release && cmake --build /tmp/b'`.

## Traps

- **Do not write to `std::cout`.** The binary's stdout is the runner protocol, and every
  line on it must be a JSON record; log to `std::cerr`.
- **No negated literal as an output leaf**: `b.Not().index()` is negative and is an
  `error`. Output the positive variable.
- **No `Build` overload or namespace**: a different signature, or `Build` inside a
  namespace, fails to link (`compilation_error`).

## Example

The pilot fixture [tests/fixtures/model.cpp](../../tests/fixtures/model.cpp) (instance
fields `n`, `optimize`; outputs `x`, `y`):

```cpp
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"
using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  int n = instance.at("n");
  auto x = model.NewIntVar(Domain(0, n));
  auto y = model.NewIntVar(Domain(0, n));
  if (instance.at("optimize").get<bool>()) {
    model.AddGreaterOrEqual(x + y, n);
    model.Minimize(x + y);
  } else {
    model.AddEquality(x + y, n);
  }
  outputs = {{"x", x.index()}, {"y", y.index()}};
}
```
