// Knapsack: choose items to take in the backpack to maximize total value without exceeding the weight capacity.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<int> weights = instance.at("weights").get<std::vector<int>>();
  std::vector<int> values = instance.at("values").get<std::vector<int>>();
  int capacity = instance.at("capacity");
  int n = static_cast<int>(weights.size());

  // x[i] = 1 if item i is taken
  vec<IntVar*> x;
  createVars(x, n, 0, 1, true);

  vec<int> w, v;
  int total_value = 0;
  for (int i = 0; i < n; ++i) {
    w.push(weights[i]);
    v.push(values[i]);
    total_value += values[i];
  }

  // the total weight of the items in the backpack must not exceed the capacity
  int_linear(w, x, IRT_LE, capacity);

  // total value of the items taken (at most the sum of all values)
  IntVar* total = newIntVar(0, total_value);
  int_linear(v, x, IRT_EQ, total);

  // maximize the total value
  branch(x, VAR_INORDER, VAL_MAX);
  optimize(total, OPT_MAX);

  json picks = json::array();
  for (int i = 0; i < n; ++i) picks.push_back(dcp::out(x[i]));
  outputs = {{"x", picks}};
}
