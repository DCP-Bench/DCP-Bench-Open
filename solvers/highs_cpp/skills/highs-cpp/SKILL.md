---
name: highs-cpp
description: HiGHS, a mixed-integer linear programming solver used from C++ through its Highs class, covering columns and rows, integrality, objective, run(), model status, and enumerating solutions with no-goods. Use when writing, debugging or explaining HiGHS C++ code for MIP or LP models, linearising logic, all-different, products, min/max or absolute values for it, or choosing big-M constants.
license: MIT
compatibility: Requires a C++17 compiler, CMake 3.15+ and HiGHS 1.15.1 built from source (github.com/ERGO-Code/HiGHS, MIT). No key, no size limits.
metadata:
  domain: optimisation
  solver: highs
  paradigm: mip
---

# HiGHS (C++)

HiGHS solves linear programs and mixed-integer linear programs. The C++ class `Highs` takes
columns (variables) and rows (linear constraints) one call at a time, then `run()` solves.
Every constraint must be linear: a disjunction, an all-different, a product of two variables or
a logical condition must be written as rows with binary columns and big-M constants. HiGHS
keeps no solution pool and does not enumerate: each solution is found by a new solve.

Docs: [C++ interface](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/docs/src/interfaces/cpp/library.md)
(source in the repository, v1.15.1), [class declaration](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/Highs.h),
[options with defaults](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/lp_data/HighsOptions.h),
[status enums](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/lp_data/HConst.h).

## Contents
- [Install](#install) · [Quick start](#quick-start) · [Modelling](#modelling) · [Patterns](#linearising-logic)
- [Solving](#solving) · [All solutions](#all-solutions) · [Common issues](#common-issues) · [Further reading](#further-reading)
- Examples: [assignment](assets/satisfy-assignment/README.md), [all solutions](assets/all-solutions-no-good/README.md),
  [knapsack](assets/maximise-knapsack/README.md), [scheduling](assets/minimise-big-m-scheduling/README.md),
  [abs, max, product](assets/min-max-abs-product/README.md), [all different](assets/alldifferent-binaries/README.md),
  [infeasible](assets/infeasible-status/README.md), [JSON data](assets/json-data/README.md)

## Install

Build HiGHS from source (needs git, CMake 3.15+, a C++17 compiler). Tested with v1.15.1 (commit `04024d7`), g++ 12.2:

```bash
git clone --depth 1 --branch v1.15.1 https://github.com/ERGO-Code/HiGHS.git
cmake -S HiGHS -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$HOME/highs" \
      -DBUILD_SHARED_LIBS=OFF -DBUILD_TESTING=OFF -DBUILD_EXAMPLES=OFF -DBUILD_CXX_EXE=OFF -DZLIB=OFF
cmake --build build -j4 && cmake --install build
export HIGHS_PREFIX="$HOME/highs"
```

Build an example with `g++ -std=c++17 -O2 model.cpp -o model -I"$HIGHS_PREFIX/include/highs" -L"$HIGHS_PREFIX/lib" -lhighs -lpthread && ./model`.
Headers are in `include/highs/`, so include them as `"Highs.h"`. The JSON example also needs `nlohmann-json3-dev`.
Verify: the Quick start prints `Objective: 3`. Docs: [installation](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/docs/src/installation.md).

## Quick start

```cpp
// Minimise x + 2y over integers 0..4 with x + y >= 3.
#include <cmath>
#include <cstdio>
#include "Highs.h"

int main() {
  Highs h;
  h.setOptionValue("output_flag", false);
  h.setOptionValue("mip_rel_gap", 0.0);            // OPTIMAL then means proven
  h.addVar(0, 4); h.addVar(0, 4);                  // columns 0 (x) and 1 (y)
  h.changeColIntegrality(0, HighsVarType::kInteger);
  h.changeColIntegrality(1, HighsVarType::kInteger);
  h.changeColCost(0, 1); h.changeColCost(1, 2);
  h.changeObjectiveSense(ObjSense::kMinimize);
  HighsInt cols[2] = {0, 1}; double coefs[2] = {1, 1};
  h.addRow(3, kHighsInf, 2, cols, coefs);          // 3 <= x + y
  h.run();
  if (h.getModelStatus() == HighsModelStatus::kOptimal)
    std::printf("Objective: %.0f\n", std::round(h.getInfo().objective_function_value));
}
```

## Modelling

Columns are numbered in `addVar` order: the first is 0. Rows take index and value arrays.

| Need | API |
|---|---|
| continuous column | [`addVar(lower, upper)`](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/Highs.h) (`-kHighsInf`/`kHighsInf` for no bound) |
| integer or binary column | `addVar(0, 1)` then [`changeColIntegrality(col, HighsVarType::kInteger)`](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/Highs.h) |
| linear row `lo <= sum a_j x_j <= hi` | [`addRow(lo, hi, nnz, index, value)`](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/Highs.h); `=` is `lo == hi`, `<=` has `lo = -kHighsInf` |
| objective coefficient | [`changeColCost(col, c)`](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/Highs.h) |
| minimise / maximise | [`changeObjectiveSense(ObjSense::kMinimize / kMaximize)`](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/Highs.h) |
| constant in the objective | [`changeObjectiveOffset(d)`](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/Highs.h); `getInfo().objective_function_value` includes it |
| change a bound | [`changeColBounds(col, lo, hi)`](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/Highs.h) |
| number of columns | [`getNumCol()`](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/Highs.h) (the next `addVar` returns this) |
| read a column's bounds or integrality back | [`getLp()`](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/Highs.h): `col_lower_`, `col_upper_`, `integrality_` |

Use `kHighsInf` (infinity, `+inf` in double). A row with no entries and bounds that exclude zero makes the model infeasible.
Pass integer counts as `HighsInt` (32-bit on this build) and bounds as `double`.

## Linearising logic

Start each block of rows with a `//` comment in the problem statement's words, not the HiGHS call
(`// every row holds different values`).
Let `M` be a big-M constant computed from the data, not a guess (see the last row).

| Pattern | Rows |
|---|---|
| one-hot: exactly one of `b_1..b_k` | `sum b_i = 1` |
| at most one | `sum b_i <= 1` |
| `b = 1` implies `a x <= r` | `a x <= r + M (1 - b)`, i.e. `a x + M b <= r + M` |
| `b = 1` implies `a x >= r` | `a x >= r - M (1 - b)` |
| `b = (x >= r)`, integer x in `lo..hi` | `x >= r b + lo (1 - b)` and `x <= (r - 1) + (hi - r + 1) b`; exact with the bounds as M |
| disjunction `a x <= r` or `c x <= s` | binary `b`: `a x <= r + M b`, `c x <= s + M (1 - b)` |
| `x != v` for integer x in `lo..hi` | binaries `b1`, `b2` with `b1 + b2 >= 1`; `x <= v - 1 + (hi - v + 1) b1`; `x >= v + 1 - (v + 1 - lo) b2` |
| all different `x_1..x_n` in `lo..hi` | `y[i][v]` binary: `x_i = sum v y[i][v]`, `sum_v y[i][v] = 1`, `sum_i y[i][v] <= 1` (see [example](assets/alldifferent-binaries/README.md)) |
| product `p = b1 b2` (binaries) | `p <= b1`, `p <= b2`, `p >= b1 + b2 - 1`, `0 <= p <= 1` |
| product `p = x y`, x integer in `lo..hi`, y binary | `p <= hi y`, `p >= lo y`, `p <= x - lo (1 - y)`, `p >= x - hi (1 - y)` (p is x when y = 1, else 0) |
| `z = max(x_1..x_k)` | `z >= x_i` for all i; to force equality under minimisation, also `z <= x_i + M (1 - b_i)` with `sum b_i = 1` |
| `z = min(x_1..x_k)` | `z <= x_i` for all i; to force equality under maximisation, `z >= x_i - M (1 - b_i)`, `sum b_i = 1` |
| `z = |x|` | `z >= x`, `z >= -x`; minimising the objective needs nothing more; to force equality under maximisation add `z <= x + M b`, `z <= -x + M (1 - b)`, `b` binary |
| strict `x < y` (integers) | `x + 1 <= y` |
| big-M from data | `M = sum over the terms of max(|a_j|) * max(|bound_j|) + |r|`, computed in the program from the instance |

Choose M from the data: the smallest value with `a x` at its extremes over the column bounds, plus the
right-hand side. A large M ruins the LP relaxation and slows the proof. Tiny M cuts off solutions. With
a schedule, the total work bounds every start in an optimal left-shifted schedule, which is safe.

## Solving

Status and parameters: [status enum](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/lp_data/HConst.h),
[options](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/lp_data/HighsOptions.h).

| `getModelStatus()` | Meaning |
|---|---|
| `kOptimal` | proven optimal when `mip_rel_gap` and `mip_abs_gap` are zero (their defaults are 1e-4 and 1e-6); the solution is in `getSolution().col_value` |
| `kInfeasible` | no solution |
| `kUnboundedOrInfeasible` | a MIP with an unbounded objective is reported this way; solve again with the objective cleared to decide |
| `kUnbounded` | the objective is unbounded |
| `kTimeLimit` | time limit reached before the proof; the result is not proven, so do not report it as optimal |
| `kNotset` | HiGHS stopped at a short time limit before setting a status (seen with a 0.2 s limit); treat as a time limit |
| `kModelEmpty` | the model has no columns; a feasible empty model reports this |

`run()` returns `HighsStatus::kOk` for an infeasible model; check `getModelStatus()`, not `run()`.
Read values with `getSolution().col_value` (doubles: round them, e.g. `std::lround`; a binary is `lround(v) == 1`).
`modelStatusToString(status)` (a `Highs` member, returns `std::string`) gives the status name.

A model with no objective (all costs zero, the default) is a satisfaction problem: `run()` returns any feasible
point and the status is `kOptimal`.

Options used by the examples (`setOptionValue`): `output_flag` (`false`: silent), `threads` (default 0 = automatic; use `HighsInt{1}`),
`mip_rel_gap` and `mip_abs_gap` (set both to `0.0`), `time_limit` (seconds, default infinite), `random_seed` (default 0).
Option defaults come from `HighsOptions.h`, not from the online docs.

## All solutions

HiGHS has no solution pool. To list solutions of a satisfaction problem, solve, record the values `v_i` of the
integer columns `x_i` (with bounds `lo_i..hi_i`), add a no-good, and solve again until `kInfeasible`:

- for each column with `v_i > lo_i`, a binary `below_i` with `x_i + (hi_i - v_i + 1) below_i <= hi_i`
  (`below_i = 1` forces `x_i <= v_i - 1`);
- for each column with `v_i < hi_i`, a binary `above_i` with `x_i - (v_i + 1 - lo_i) above_i >= lo_i`
  (`above_i = 1` forces `x_i >= v_i + 1`);
- one row: the sum of all these binaries `>= 1`.

A binary column (`lo = 0`, `hi = 1`) needs only one indicator: the one that flips it (`x = 1` gives `below`, `x = 0` gives `above`).
If no indicator is created, every column is fixed and the enumeration is complete. Full code in
[the example](assets/all-solutions-no-good/README.md).

For all optimal solutions: solve, record the optimum `z` from `getInfo().objective_function_value`. Write the
objective as a row over the same columns, `sum_j c_j x_j + offset` (the cost coefficients and the offset from
`changeObjectiveOffset`), and add it as `z - 1e-5 <= row <= z + 1e-5`. Then enumerate with the same no-goods.
Only integer columns that the reported answer depends on need no-goods; each solve costs one more round, so keep
the enumerated count small.

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| `kOptimal` but a result is off by a fraction | `mip_rel_gap` default 1e-4 | set `mip_rel_gap` and `mip_abs_gap` to 0 |
| `run()` returns `kOk` but the model is infeasible | status is in the model, not the return value | check `getModelStatus()` |
| `kUnboundedOrInfeasible` on a MIP | HiGHS does not say which | re-solve with the objective set to zero; no solution means infeasible |
| time limit with no proof | LP relaxation weak | tighter big-M, binary formulation, stronger rows |
| a value printed as 2.99999 | solver tolerance (`mip_feasibility_tolerance` default 1e-6) | `std::lround` before printing |
| wrong sign on a maximisation objective | coefficients were set for minimisation | `changeObjectiveSense(ObjSense::kMaximize)` and check the cost signs |
| constant missing from the objective | offset not set | `changeObjectiveOffset` |
| column index out of range | columns numbered in `addVar` order from 0 | use `getNumCol()` before each `addVar` |

## Further reading

- C++ interface guide: [library.md](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/docs/src/interfaces/cpp/library.md) and [examples.md](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/docs/src/interfaces/cpp/examples.md)
- Full API: [Highs.h](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/Highs.h)
- Options and defaults: [HighsOptions.h](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/highs/lp_data/HighsOptions.h)
- Example programs: [call_highs_from_cpp.cpp](https://github.com/ERGO-Code/HiGHS/blob/v1.15.1/examples/call_highs_from_cpp.cpp)
