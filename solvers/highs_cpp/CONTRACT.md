# highs_cpp: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how HiGHS (C++ API)
expresses it. The standalone solver skill is [highs-cpp](skills/highs-cpp/SKILL.md): it teaches
the `Highs` API. Runner: [run.py](run.py) hands the submission to the C++ driver
[driver.cpp](cpp/driver.cpp), which the image builds with [CMakeLists.txt](cpp/CMakeLists.txt).
The helpers the submission uses are in [dcp.h](cpp/dcp.h).

## Submission file

One C++ file, `model.cpp`. It starts with `#include "dcp.h"` and may use `Highs`, the
standard library and `nlohmann/json.hpp` (the instance is a `json`). It must not define
`main`, read or write files, print to stdout, or include other files of yours (only the one
submission file is staged).

## Entrypoint

```cpp
#include "dcp.h"
void build(const json& instance, Highs& h, dcp::Outputs& out);
```

The driver calls `build` once, with an empty `Highs` object and an empty `dcp::Outputs`. The
submission adds columns and rows to `h` with the HiGHS API, and registers its outputs and its
objective on `out`. It must not call `h.run()`. Exceptions thrown from `build` are reported as
`error` with the exception's message.

Helpers in `dcp.h` (namespace `dcp`):

| Helper | Meaning |
|---|---|
| `Lin` | affine expression over columns: `constant + sum coef * column`; a number converts to a constant |
| `Lin::col(k)` | column `k` (`HighsInt`, the order of `addVar` calls, from 0) |
| `new_var(h, lo, hi, integer = true)` | adds a column with bounds and integrality, returns it as a `Lin` |
| `add_row(h, expr, lo, hi)` | adds `lo <= expr <= hi`; the constant of `expr` moves to the bounds |
| `out.add(name, value)` | registers an output: a `Lin` (number, column, expression) |
| `out.add(name, vector)` | registers a nested `std::vector` of `Lin` (any depth); the output is a nested list |
| `out.minimize(expr)` / `out.maximize(expr)` | the objective; at most one call |

Raw HiGHS calls (`addVar`, `addRow`, `changeColIntegrality`) work too; then columns are
`HighsInt` indices and the outputs are built from `Lin::col`.

## Instance

`instance` is the instance JSON as `nlohmann::json`, keys as in the brief. Read every size from it:
`instance.at("n").get<int>()`, `instance.at("rows")`, and so on. Arrays are nested
`json` arrays, 0-based as stored. Extra keys (`name`, `note`) are ignored.

## Outputs

Each output name maps to an integer, a `Lin`, or a nested `std::vector` of them. A `Lin` must
take integer values on the solution: the value is rounded, and a value more than `1e-5` away
from an integer is an error (`Declared outputs must be integers`). `-0` is reported as `0`.
Booleans are reported as `0`/`1`: use a binary column (see [flag in the readiness fixture](readiness_test.py)).

Values are doubles inside HiGHS: integers up to about `2^53` are exact in a solution, but
HiGHS's tolerances (`primal_feasibility_tolerance` 1e-7, `mip_feasibility_tolerance` 1e-6)
mean a value near `1e9` is only as exact as the tolerance allows. Verified: `5e9` and
`3.1e10` as fixed columns are reported exactly.

## Objective

Declared with `out.minimize(expr)` or `out.maximize(expr)`. The driver applies it: every
column cost is set to the expression's coefficient (0 where the expression has none), the
constant goes to `changeObjectiveOffset`, and the sense to `changeObjectiveSense`. A
submission that sets costs on `h` itself has them overwritten. No objective means a
satisfaction problem.

## Solving

The driver sets these options after `build` (a submission cannot change them):

| Option | Value | Why |
|---|---|---|
| `output_flag`, `log_to_console` | `false` | silence; stdout goes to stderr anyway |
| `threads` | `1` | one thread |
| `mip_rel_gap`, `mip_abs_gap` | `0`, `0` | HiGHS defaults are 1e-4 and 1e-6; `kOptimal` must mean proven |
| `random_seed` | `0` | fixed |
| `time_limit` | the time left before the deadline, set before each solve | the deadline is 0.3 s inside the budget |

Status mapping from `getModelStatus()`:

| HiGHS status | Result |
|---|---|
| `kOptimal` with a feasible point | a solution; proven optimal |
| `kModelEmpty` | a solution (no columns) |
| `kInfeasible` | `unsat` |
| `kUnboundedOrInfeasible` | solved again with the objective cleared: infeasible gives `unsat` (or `complete` during enumeration), feasible gives `error` ("The objective is unbounded") |
| `kUnbounded` | `error` ("The objective is unbounded") |
| `kTimeLimit`, or `kNotset` at the deadline | `timeout`, with "Candidate optimum was not proven" for an objective |
| `kNotset`/`kUnknown` before the deadline, `kMemoryLimit` and any other | `error` with the status name |
| `run()` returns `kError` | `error` |

Enumeration (`solution_limit > 1`): the first solution is kept if it is optimal. For an objective,
the objective is pinned to the optimum within `1e-5`. Each further solution is excluded with a
no-good over the integer columns that the outputs are built from: a binary below and a binary
above each current value, big-M from the column's own bounds, and at least one indicator on.
Repeated output values are not emitted twice. `complete` when no further assignment exists.
Enumeration needs every such column to be integer with finite bounds; otherwise the status is
`unsupported` with the reason. Values are emitted only after the optimum is proven.

Time: the driver's deadline is `execution_timeout - 0.3 s` (at least 0.1 s), and every solve
gets the time left. `timeout` reports a solve cut by the deadline; no unproven optimum is emitted.

## Compilation

The image compiles `model.cpp` with CMake (`/opt/cpp/CMakeLists.txt`, C++17, `-DCMAKE_BUILD_TYPE=Release`)
under the compilation budget, with `driver.cpp` in the same executable. A compile error is
`compilation_error`, with "see stderr".

## Environment

- Image `dcp-eval/highs_cpp:v1`, base `python:3.12.11-slim-bookworm` (digest pinned in the Dockerfile).
- HiGHS 1.15.1, built from the `v1.15.1` tag (commit `04024d701f79feb8e2f18bc3df0dffc04ef05088`, checked
  in the Dockerfile) as a static library (`libhighs.a`) into `/opt/highs`; `CMAKE_PREFIX_PATH=/opt/highs`.
  The headers are in `/opt/highs/include/highs`. The build used `-DZLIB=OFF` (HiGHS's optional zlib
  support; the integration never reads files).
- g++ 12.2.0, cmake 3.25.1, make 4.3, nlohmann-json 3.11.2 (`nlohmann/json.hpp` is available; the
  driver uses it to read the request).
- Run by the evaluator with `--network=none --read-only --user=65534:65534 --cap-drop=ALL` and a 512 MB
  `/tmp` tmpfs (the build directory). Nothing else is writable.
- Not available: other solvers, Python packages in the solve path (the Python interpreter only runs the runner).
- HiGHS's own log messages are not captured: with `output_flag` off, a HiGHS error comes back as its
  status name and the driver's text, not the log line.

## Traps

- `HighsInt` is 32-bit in this build (`HIGHSINT64` off): column counts and indices above 2^31 are not
  possible.
- Only the status `kOptimal` proves an optimum; `kTimeLimit` never does. With no time limit set by the
  model, HiGHS runs until proven or until the driver's deadline.
- A column used by an output that is continuous or unbounded makes enumeration `unsupported`. A single
  solution still works, but an output whose value is not within `1e-5` of an integer is an `error`.
- A model whose objective is unbounded is `error`, not `unsat`.
- Declared outputs must follow the description's conventions (1-based numbers, Boolean as 0/1), as the
  contract requires; the driver does not shift them.
- The objective is set only by `out.minimize/maximize`; calling `changeColCost` or
  `changeObjectiveSense` on `h` has no effect.

## Example

The pilot fixture [model_highs_cpp.cpp](../../tests/fixtures/model_highs_cpp.cpp) (instance fields `n`,
`optimize`; outputs `x`, `y`):

```cpp
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n");
  dcp::Lin x = dcp::new_var(h, 0, n);
  dcp::Lin y = dcp::new_var(h, 0, n);
  if (instance.at("optimize").get<bool>()) {
    dcp::add_row(h, x + y, n, kHighsInf);
    out.minimize(x + y);
  } else {
    dcp::add_row(h, x + y, n, n);
  }
  out.add("x", x);
  out.add("y", y);
}
```
