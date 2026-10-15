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
`LinearExpr`. A floating-point objective is refused (`unsupported`). The driver accepts
only `OPTIMAL`; for further solutions it clears the objective, adds `objective ==
optimum`, and forbids the reported tuple of output variables before each re-solve.

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
nlohmann/json 3.11.2. The driver solves with one search worker and
`keep_all_feasible_solutions_in_presolve` on; the model cannot change solver parameters.

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
