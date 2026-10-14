// Capital budgeting: choose investments to maximize total net present value within a cash budget.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int budget = instance.at("budget");
  std::vector<int> cash_flow = instance.at("cash_flow").get<std::vector<int>>();
  std::vector<int> npv = instance.at("npv").get<std::vector<int>>();
  int n = static_cast<int>(cash_flow.size());

  int total_npv = 0;
  for (int v : npv) total_npv += v;

  // x[i] = 1 if investment i is chosen (0/1 integer, exported as a boolean)
  vec<IntVar*> x;
  createVars(x, n, 0, 1, true);

  vec<int> outflow, gain;
  for (int i = 0; i < n; ++i) {
    outflow.push(cash_flow[i]);
    gain.push(npv[i]);
  }

  // the sum of the cash outflows of all chosen investments must not exceed the budget
  int_linear(outflow, x, IRT_LE, budget);

  // z is the total net present value of the chosen investments
  IntVar* z = newIntVar(0, total_npv);
  int_linear(gain, x, IRT_EQ, z);

  // try the investments in order; maximize the total NPV
  branch(x, VAR_INORDER, VAL_MAX);
  optimize(z, OPT_MAX);

  json chosen = json::array();
  for (int i = 0; i < n; ++i) chosen.push_back(dcp::out(x[i]));
  outputs = {{"x", chosen}, {"z", dcp::out(z)}};
}
