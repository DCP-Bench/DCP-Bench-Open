---
name: ortools-cp-sat-cpp
description: OR-Tools CP-SAT, Google's constraint programming and optimisation solver, used from C++ through its CpModelBuilder API. Use when writing, debugging or explaining CP-SAT models in C++, installing OR-Tools for C++ with CMake, or enumerating all solutions or all optimal solutions with it.
license: Apache-2.0
compatibility: Requires a C++17 compiler (tested with g++ 12.2), CMake 3.18+ and the OR-Tools 9.15 C++ binary archive (free, no key or account; tested on Debian 12 x86_64)
metadata:
  domain: constraint-programming
  solver: ortools-cp-sat
  paradigm: cp
---

# OR-Tools CP-SAT (C++)

CP-SAT is a finite-domain constraint solver that combines propagation with clause learning. You declare integer and Boolean variables on a `CpModelBuilder`, add linear and global constraints, optionally add one objective, then call `Solve`. Two rules to keep in mind: every variable has a finite integer domain, and the objective is an integer linear expression (scale money to whole cents).

Official guide: [CP-SAT solver](https://developers.google.com/optimization/cp/cp_solver) ([Markdown](https://developers.google.com/optimization/cp/cp_solver.md)). Builder API: [`cp_model.h`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h), whose comments are the reference.

## Contents
- [Install](#install)
- [Quick start](#quick-start)
- [Modelling](#modelling)
- [Reading instance data](#reading-instance-data)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Common issues](#common-issues)
- [Further reading](#further-reading)

## Install

Official guide: [OR-Tools C++ binary install](https://developers.google.com/optimization/install/cpp/binary_linux). You need `g++` with C++17 and `cmake` 3.18 or newer (Debian: `sudo apt install build-essential cmake`; ask before using `sudo`).

```bash
curl -fL -o or-tools.tar.gz https://github.com/google/or-tools/releases/download/v9.15/or-tools_amd64_debian-12_cpp_v9.15.6755.tar.gz
echo 'b2c9870c8778eeb26c98742402da17da039c058fca7eca87be5c90832b04153c  or-tools.tar.gz' | sha256sum -c -
mkdir -p "$HOME/or-tools" && tar xzf or-tools.tar.gz -C "$HOME/or-tools" --strip-components=1
export CMAKE_PREFIX_PATH="$HOME/or-tools"   # CMake reads this variable; no -D needed
```

The commands above fetch the Debian 12 x86_64 archive (the one tested). On other systems take the C++ archive for yours from the [v9.15 release page](https://github.com/google/or-tools/releases); the steps are the same, the checksum line is not.

The archive bundles its own Abseil, protobuf and Boost, so the compiler and CMake are the only tools to install. Verify with the Quick start below: it prints `Objective: 12`.

If OR-Tools is already unpacked somewhere (a container or a shared install), point `CMAKE_PREFIX_PATH` at that directory and add its `lib/` to `LD_LIBRARY_PATH`, then skip the download and go to the Quick start. Check with `echo $CMAKE_PREFIX_PATH`; if it is empty, use the commands above.

## Quick start

`model.cc`:

```cpp
#include <cstdint>
#include <iostream>

#include "ortools/sat/cp_model.h"
#include "ortools/sat/cp_model_solver.h"

using namespace operations_research;
using namespace operations_research::sat;

int main() {
  // Maximise 3x + 2y for integers 0 <= x, y <= 4 with x + y <= 4 and x + 3y <= 6.
  CpModelBuilder model;
  const IntVar x = model.NewIntVar(Domain(0, 4));
  const IntVar y = model.NewIntVar(Domain(0, 4));
  model.AddLessOrEqual(x + y, 4);
  model.AddLessOrEqual(x + 3 * y, 6);
  model.Maximize(3 * x + 2 * y);

  const CpSolverResponse response = Solve(model.Build());
  if (response.status() == CpSolverStatus::OPTIMAL) {
    std::cout << "Objective: " << static_cast<int64_t>(response.objective_value()) << "\n";
    std::cout << "x = " << SolutionIntegerValue(response, x) << ", y = "
              << SolutionIntegerValue(response, y) << "\n";
  } else {
    std::cout << "Status: " << CpSolverStatus_Name(response.status()) << "\n";
  }
  return 0;
}
```

`CMakeLists.txt` next to it:

```cmake
cmake_minimum_required(VERSION 3.18)
project(model LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
find_package(ortools CONFIG REQUIRED)
add_executable(model model.cc)
target_link_libraries(model PRIVATE ortools::ortools)
```

```bash
cmake -S . -B build && cmake --build build && ./build/model
```

Several programs in one project: list their names, and CMake builds each from `<name>.cc` into `build/bin`.

```cmake
set(PROGRAMS knapsack copy)
foreach(program IN LISTS PROGRAMS)
  add_executable(${program} ${program}.cc)
  target_link_libraries(${program} PRIVATE ortools::ortools)
  set_target_properties(${program} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
endforeach()
```

Worked examples, one folder each under `assets/` with `model.cc`, `CMakeLists.txt` and a README: `satisfy-latin-square` (satisfy), `all-solutions-subset-sum`, `all-optimal-committee`, `maximise-production-plan`, `minimise-assignment`, `infeasible-pigeonhole`, `scheduling-cumulative` (cumulative resource) and `no-overlap-jobshop` (one machine per no-overlap constraint).

## Reading instance data

A program that solves a data file receives its path as `argv[1]`. This skill parses it with nlohmann/json, header `/usr/include/nlohmann/json.hpp` from the Debian package `nlohmann-json3-dev` (`sudo apt install nlohmann-json3-dev`, asking before `sudo`). Link it through CMake:

```cmake
find_package(nlohmann_json CONFIG REQUIRED)
target_link_libraries(model PRIVATE ortools::ortools nlohmann_json::nlohmann_json)
```

```cpp
#include <cstdint>
#include <fstream>
#include <iostream>
#include <vector>

#include <nlohmann/json.hpp>

int main(int argc, char** argv) {
  if (argc < 2) {
    std::cerr << "usage: " << argv[0] << " INSTANCE.json\n";
    return 2;
  }
  std::ifstream in(argv[1]);
  const nlohmann::json instance = nlohmann::json::parse(in);
  const auto weights = instance.at("weights").get<std::vector<int64_t>>();
  const int64_t capacity = instance.at("capacity").get<int64_t>();
  // ... build the model from these values
}
```

`parse` throws on malformed JSON and `at` throws on a missing key, so a failure stops the program with an exception rather than a wrong answer. The full program is verified by building with `find_package(nlohmann_json)`; it prints `Value: 10` for weights `[3, 4, 5]`, values `[4, 5, 6]` and capacity `8`.

## Modelling

Full list: [`cp_model.h`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h).

| Need | API |
|---|---|
| Integer variable with bounds | [`NewIntVar(Domain(lo, hi))`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) |
| Domain with holes | [`Domain::FromValues({-1, 1})`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) |
| Boolean variable | [`NewBoolVar()`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h); a `BoolVar` enters sums directly: `total += weight * take[i]` |
| Constant as a variable | [`NewConstant(k)`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) |
| Linear (in)equality | [`AddEquality`, `AddNotEqual`, `AddLessOrEqual`, `AddLessThan`, `AddGreaterOrEqual`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) |
| Linear value in a set | [`AddLinearConstraint(expr, Domain::FromValues({3, 4, 7}))`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) |
| All different | [`AddAllDifferent(std::vector<LinearExpr>)`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) |
| Element (array read at a variable index) | [`AddElement`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h), see [Common issues](#common-issues) |
| Absolute value, min, max | [`AddAbsEquality`, `AddMinEquality`, `AddMaxEquality`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) |
| Product, modulo | [`AddMultiplicationEquality`, `AddModuloEquality`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h); chain a product two factors at a time, each intermediate bounded |
| Boolean clauses | [`AddBoolOr`, `AddBoolAnd`, `AddImplication`, `AddAtMostOne`, `AddExactlyOne`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) |
| Reification | [`.OnlyEnforceIf(lit)`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h), posted in both directions; see below |
| Regular language | [`AddAutomaton(exprs, start, finals)`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) then [`.AddTransition(tail, head, label)`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) per arc |
| Intervals and no-overlap | [`NewFixedSizeIntervalVar(start, size)`, `NewIntervalVar(start, size, end)`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h); [`AddNoOverlap(std::vector<IntervalVar>)`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) takes the intervals of one machine per call, see `no-overlap-jobshop` |
| Cumulative resource | [`AddCumulative(capacity)`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) then [`.AddDemand(interval, demand)`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) |
| 2-D no-overlap | [`AddNoOverlap2D()`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) then `.AddRectangle(x_interval, y_interval)` |
| Minimise / maximise | [`Minimize(expr)` / `Maximize(expr)`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h); at most one objective |

Reification needs both directions, or the indicator is free to take the value that suits the search:

```cpp
BoolVar hit = model.NewBoolVar();
model.AddEquality(x[i], value).OnlyEnforceIf(hit);
model.AddNotEqual(x[i], value).OnlyEnforceIf(hit.Not());
```

This counts occurrences (`sum(x == v) == k` is a sum of `hit` indicators), and a disjunction of constraints is one `AddBoolOr` over their indicators.

## Solving

Status values: [`CpSolverStatus`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.proto). Parameters: [`sat_parameters.proto`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/sat_parameters.proto).

| Status | Meaning |
|---|---|
| `OPTIMAL` | Solution found; for an optimisation, optimality is proven |
| `FEASIBLE` | Solution found but not proven optimal (time limit reached) |
| `INFEASIBLE` | Proven: no solution exists |
| `UNKNOWN` | Limit reached before any solution or proof |
| `MODEL_INVALID` | The model is malformed; read `ValidateCpModel(model.Build())` |

Read values only after checking the status is `OPTIMAL` or `FEASIBLE`.

```cpp
SatParameters parameters;
parameters.set_max_time_in_seconds(10.0);
parameters.set_num_workers(8);
parameters.set_random_seed(42);
parameters.set_log_search_progress(true);   // the search log goes to stdout
const CpSolverResponse response = SolveWithParameters(model.Build(), parameters);
```

| Need | Call |
|---|---|
| Value of an `IntVar` or `LinearExpr` | `SolutionIntegerValue(response, expr)` |
| Value of a `BoolVar` | `SolutionBooleanValue(response, b)` |
| Objective and its bound | `response.objective_value()` (a double), `response.best_objective_bound()` |
| Why a model is invalid | `ValidateCpModel(model.Build())` (`ortools/sat/cp_model_checker.h`); empty when valid |


## All solutions

Enumerate with a solution observer and one worker. Every variable in the model is part of the solution, so enumerate over decision variables only (see the first issue below). The snippet needs the same `using` lines as the Quick start, and these headers:

```cpp
#include "ortools/sat/cp_model.h"
#include "ortools/sat/cp_model_solver.h"
#include "ortools/sat/model.h"
#include "ortools/sat/sat_parameters.pb.h"

Model enumerator;
int count = 0;
enumerator.Add(NewFeasibleSolutionObserver([&] (const CpSolverResponse& r) {
  ++count;   // read the decision variables of r here
}));
SatParameters parameters;
parameters.set_enumerate_all_solutions(true);
parameters.set_num_workers(1);
enumerator.Add(NewSatParameters(parameters));
const CpSolverResponse response = SolveCpModel(model.Build(), &enumerator);
```

Pattern and runnable code: `all-solutions-subset-sum`. Reference: [`sat_parameters.proto`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/sat_parameters.proto) (`enumerate_all_solutions`), [sample programs](https://github.com/google/or-tools/tree/v9.15/ortools/sat/samples).

**All optimal solutions:** solve once to get the optimum `z*`. Build a second model from scratch with the same constraints, `AddEquality(objective_expr, z*)` and no objective, then enumerate it as above. A model that still carries the objective is optimised, not enumerated. Pattern and code: `all-optimal-committee`.

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| Duplicate solutions from enumeration | Auxiliary variables are not fixed by the decision variables, so each decision tuple repeats once per auxiliary value | Remove the auxiliary variables from the enumerated model, or count distinct values of the decision variables |
| Enumeration returns fewer solutions than exist | More than one worker: with 8 workers a 6-solution model returned 5 | `set_num_workers(1)` with `set_enumerate_all_solutions(true)` |
| Compile error listing many `AddElement` candidates | `AddElement` takes a span of `LinearExpr` (or of `int64_t` constants), not of `IntVar`; a `std::vector<IntVar>` converts to neither | Convert once: `const std::vector<LinearExpr> exprs(vars.begin(), vars.end());`. `AddAllDifferent` and `AddMaxEquality` need the same conversion for expressions such as `queens[i] - i` |
| Two-dimensional table indexed by two variables | Nested element constraints, or an `AddElement` on the wrong axis | Flatten the table into one `std::vector<LinearExpr>` of width `w`, add `AddEquality(cell, w * row + col)`, then one `AddElement(cell, ...)` |
| Indicator takes either value | Reification posted in one direction only | Post the constraint under `lit` and its negation under `lit.Not()`; see [Modelling](#modelling) |
| `MODEL_INVALID` | Malformed model, for example a domain with `lo > hi` | Print `ValidateCpModel(model.Build())` and fix the named variable or constraint |
| `FEASIBLE` instead of `OPTIMAL` for an optimisation | Time limit reached; optimality not proven | Raise `set_max_time_in_seconds`, or accept the value and say it is not proven |
| `AddModuloEquality` or `AddMultiplicationEquality` misbehaves | The target or an intermediate of a product has no finite domain covering its true range | Give each target and intermediate a bounded `Domain` |
| Objective with decimal costs | CP-SAT works on integers; the floating-point `Minimize` overload scales coefficients internally | Multiply costs by 100 (or 1000) yourself and keep the objective integer |
| Compile error: `Model`, `NewFeasibleSolutionObserver` or `NewSatParameters` not declared | The enumeration headers are missing | Include `ortools/sat/model.h` and `ortools/sat/sat_parameters.pb.h` with the other two headers, as in [All solutions](#all-solutions) |
| Job shop reports makespan 23 where the optimum is 11 | One `AddNoOverlap` over the intervals of all machines, which also forbids overlap between machines | One `AddNoOverlap` call per machine, each over that machine's intervals; `no-overlap-jobshop` does this |
| `fatal error: nlohmann/json.hpp: No such file or directory` | nlohmann/json not installed, or not linked | Install `nlohmann-json3-dev`, then `find_package(nlohmann_json CONFIG REQUIRED)` and link `nlohmann_json::nlohmann_json`; see [Reading instance data](#reading-instance-data) |

## Further reading

- Solver guide: [CP-SAT solver](https://developers.google.com/optimization/cp/cp_solver) ([Markdown](https://developers.google.com/optimization/cp/cp_solver.md))
- API: [`cp_model.h`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.h) for every builder method, [`cp_model.proto`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.proto) for statuses, [`sat_parameters.proto`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/sat_parameters.proto) for parameters
- Examples: [official samples](https://github.com/google/or-tools/tree/v9.15/ortools/sat/samples), starting with `cp_sat_example.cc` and `search_for_all_solutions_sample_sat.cc`
- Install: [OR-Tools C++ binary](https://developers.google.com/optimization/install/cpp/binary_linux)
