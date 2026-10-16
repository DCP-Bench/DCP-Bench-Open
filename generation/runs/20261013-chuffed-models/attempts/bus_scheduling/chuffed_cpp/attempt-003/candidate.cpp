// Bus scheduling: minimize the buses needed so that every 4-hour interval of the day has enough buses.
// A bus works 8 hours, so a bus that starts in interval i is on duty in intervals i and i+1 (cyclically).
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<int> demands = instance.at("demands").get<std::vector<int>>();
  int n = static_cast<int>(demands.size());
  int total_demand = 0;
  for (int d : demands) total_demand += d;

  // x[i] = number of buses that start in interval i (no interval needs more buses than the total demand)
  vec<IntVar*> x;
  createVars(x, n, 0, total_demand);

  // buses on duty in interval i are those that start in interval i and in interval i-1 (cyclically),
  // and their number must meet the demand of interval i
  for (int i = 0; i < n; ++i) bin_linear(x[i], x[(i + n - 1) % n], IRT_GE, demands[i]);

  // the number of buses is the total number of buses started
  IntVar* total = newIntVar(0, n * total_demand);
  int_linear(x, IRT_EQ, total);
  optimize(total, OPT_MIN);

  branch(x, VAR_INORDER, VAL_MIN);

  json counts = json::array();
  for (int i = 0; i < n; ++i) counts.push_back(dcp::out(x[i]));
  outputs = {{"x", counts}};
}
