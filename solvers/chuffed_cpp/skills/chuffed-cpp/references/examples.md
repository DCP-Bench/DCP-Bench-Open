# Tested example submissions

Both files were run through the repository evaluator against
`dcp-eval/chuffed_cpp:v1` with a small CPMpy reference and two instances each.
Results are at the end. Use them as templates: a header comment naming the
problem, instance data read from `instance`, a comment above every constraint
group in the problem's words, a `branch` on the decision variables, outputs
registered with `dcp::out`.

## Satisfaction: n-queens (`n` from the instance)

Declared output `queens`: an array of `n` integers.

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
  for (int i = 0; i < n; ++i) {
    up.push(i);
    down.push(-i);
  }
  all_different_offset(up, queens);
  all_different_offset(down, queens);

  // the queens are the decision variables; fill the emptiest column first
  branch(queens, VAR_SIZE_MIN, VAL_MIN);

  json cols = json::array();
  for (int i = 0; i < n; ++i) cols.push_back(dcp::out(queens[i]));
  outputs = {{"queens", cols}};
}
```

## Optimization: 0/1 knapsack (arrays from the instance)

Declared outputs `take` (array of 0/1) and `profit`. The objective is an
auxiliary variable that is also exported, and the Boolean-like decision is a
0..1 IntVar so it needs no `bool2int`.

```cpp
// 0/1 knapsack: choose items to maximize total value without exceeding the capacity.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<int> weights = instance.at("weights").get<std::vector<int>>();
  std::vector<int> values = instance.at("values").get<std::vector<int>>();
  int capacity = instance.at("capacity");
  int n = static_cast<int>(weights.size());

  // take[i] = 1 if item i goes into the knapsack
  vec<IntVar*> take;
  createVars(take, n, 0, 1, true);

  vec<int> w, v;
  int total_value = 0;
  for (int i = 0; i < n; ++i) {
    w.push(weights[i]);
    v.push(values[i]);
    total_value += values[i];
  }

  // the total weight of the chosen items must not exceed the capacity
  int_linear(w, take, IRT_LE, capacity);

  // profit is the total value of the chosen items (bounded by the sum of all values)
  IntVar* profit = newIntVar(0, total_value);
  int_linear(v, take, IRT_EQ, profit);

  // maximize the profit; try taking items first
  branch(take, VAR_INORDER, VAL_MAX);
  optimize(profit, OPT_MAX);

  json picks = json::array();
  for (int i = 0; i < n; ++i) picks.push_back(dcp::out(take[i]));
  outputs = {{"take", picks}, {"profit", dcp::out(profit)}};
}
```

## A Boolean output

A reified Boolean is a `BoolView`; export it through a 0..1 IntVar.

```cpp
// lt = 1 exactly when x0 is smaller than x1
BoolView lt = newBoolVar();
int_rel_reif(x[0], IRT_LT, x[1], lt);
IntVar* lt_int = newIntVar(0, 1);
bool2int(lt, lt_int);
outputs = {{"lt", dcp::out(lt_int)}};
```

## Larger recipe models used to verify the cheat sheet

[recipes1.cpp](recipes1.cpp) (abs difference, max, min, reified count, Boolean output, half
reification, weighted sum, 2-D element through a flattened index, lex) and
[recipes2.cpp](recipes2.cpp) (circuit, table, cumulative, disjunctive, regular, bool_clause,
bool_linear) were accepted by the evaluator against CPMpy references. The calls
they use are marked **(tested)** in the cheat sheet.

## Evaluation record

Run with `evaluation.evaluate(path, "skilltest", "chuffed_cpp",
reference_source=REF, instances=[...], instance_count=2, solution_limit=50)`,
each reference carrying a `# Data ... # End of data` block and a literal
`solution = {...}` dictionary.


| Model | Instances | Result |
| --- | --- | --- |
| n-queens | `n` = 6 and 8, solution limit 50 | accepted; n = 6 exhausted with its 4 solutions, n = 8 stopped at the limit |
| knapsack | two instances (optimum 51 and 90) | accepted; optimum proven, one optimal solution each |
| recipes1 | `n` = 3 and 4, limit 500 | accepted; both instances exhausted (18 and 22 solutions) |
| recipes2 | `n` = 1 and 2, limit 12 | accepted; 12 solutions checked per instance, stopped at the limit |

Acceptance means no counterexample was found. A constraint that is too strong
leaves no trace, so read the comments against the problem statement as well.
