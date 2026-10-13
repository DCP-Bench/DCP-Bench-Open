# Examples

## Standalone programs (generic)

Both compiled and ran against Chuffed 0.14.0 (`g++` 12, CMake 3.25).

- [standalone_queens.cpp](standalone_queens.cpp): `queens <n> [max_solutions]`; `Problem` subclass, `all_different_offset`, `branch`, `output_vars`, `print` reading `getVal()`, status after solve. `queens 8` prints one solution, `queens 6 0` all 4, `queens 3 5` reports `=====UNSATISFIABLE=====`.
- [standalone_knapsack.cpp](standalone_knapsack.cpp): hardcoded instance; `int_linear` with weights and values, `optimize(profit, OPT_MAX)`; `print` runs on each improving solution; `engine.best_sol` is the optimum (51 for the built-in data).

CMake for both: the snippet in SKILL.md, with `foreach(name queens knapsack)` around `add_executable`/`target_*`.

## Constraint snippets (plain code)

```cpp
// lt = 1 exactly when x0 is smaller than x1 (a Boolean exposed as 0..1 IntVar)
BoolView lt = newBoolVar();
int_rel_reif(x[0], IRT_LT, x[1], lt);
IntVar* lt_int = newIntVar(0, 1);
bool2int(lt, lt_int);
```

More calls (abs difference, max, min, reified count, half reification, weighted sum, 2-D element,
lex, circuit, table, cumulative, disjunctive, regular, bool_clause, bool_linear) are in
[recipes1.cpp](recipes1.cpp) and [recipes2.cpp](recipes2.cpp). They are in DCP-Bench format
(see below) but the constraint code is plain Chuffed. The calls they use are marked **(tested)** in
the cheat sheet.

## DCP-Bench format

Only for DCP-Bench Open submissions (see the last section of SKILL.md). The same models as
`Build(instance, outputs)` with `dcp::out`; the evaluator accepted them against CPMpy references
(queens n = 6, 8; knapsack optimum 51 and 90; recipes1 n = 3, 4; recipes2 n = 1, 2).

```cpp
// N-queens: place n queens on an n x n board so that no two attack each other.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");

  // queens[i] is the row of the queen placed in column i
  vec<IntVar*> queens;
  createVars(queens, n, 0, n - 1);

  // no two queens share a row
  all_different(queens);

  // no two queens share a diagonal: queens[i] + i and queens[i] - i are all different
  vec<int> up, down;
  for (int i = 0; i < n; ++i) { up.push(i); down.push(-i); }
  all_different_offset(up, queens);
  all_different_offset(down, queens);

  // the queens are the decision variables; fill the emptiest column first
  branch(queens, VAR_SIZE_MIN, VAL_MIN);

  json cols = json::array();
  for (int i = 0; i < n; ++i) cols.push_back(dcp::out(queens[i]));
  outputs = {{"queens", cols}};
}
```

Optimization variant (knapsack, outputs `take` and `profit`): arrays from
`instance.at("weights").get<std::vector<int>>()`, the objective `profit` is an IntVar that is also
exported, `take` is a 0..1 IntVar array so no `bool2int` is needed:

```cpp
// the total weight of the chosen items must not exceed the capacity
int_linear(w, take, IRT_LE, capacity);
// profit is the total value of the chosen items
IntVar* profit = newIntVar(0, total_value);
int_linear(v, take, IRT_EQ, profit);
branch(take, VAR_INORDER, VAL_MAX);
optimize(profit, OPT_MAX);
outputs = {{"take", picks}, {"profit", dcp::out(profit)}};   // picks: json array of dcp::out(take[i])
```

A Boolean output: export `dcp::out(lt_int)` using the snippet above.
