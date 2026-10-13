// Covering problem: hire a set of workers that covers every task at minimum total hiring cost.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int nw = instance.at("nb_workers");
  int nt = instance.at("num_tasks");
  std::vector<int> cost = instance.at("Cost").get<std::vector<int>>();
  const json& qualified = instance.at("Qualified");  // qualified[t] lists the 1-based workers that can perform task t

  // hire[w] = 1 if worker w is hired; the Boolean is exported through the 0..1 integer hired[w]
  vec<BoolView> hire;
  createVars(hire, nw);
  vec<IntVar*> hired;
  for (int w = 0; w < nw; ++w) {
    IntVar* h = newIntVar(0, 1);
    bool2int(hire[w], h);
    hired.push(h);
  }

  // every task must be performed by at least one hired worker who is qualified for it
  for (int t = 0; t < nt; ++t) {
    vec<BoolView> qualified_hired;
    for (const auto& w1 : qualified.at(t)) {
      qualified_hired.push(hire[w1.get<int>() - 1]);  // worker numbers in the data are 1-based
    }
    bool_clause(qualified_hired);
  }

  // total is the hiring cost of the chosen workers
  int max_cost = 0;
  vec<int> coef;
  for (int w = 0; w < nw; ++w) {
    coef.push(cost[w]);
    max_cost += cost[w];
  }
  IntVar* total = newIntVar(0, max_cost);
  int_linear(coef, hired, IRT_EQ, total);

  // branch on the hiring decisions, cheapest workers first
  branch(hired, VAR_INORDER, VAL_MIN);
  optimize(total, OPT_MIN);

  json workers = json::array();
  for (int w = 0; w < nw; ++w) workers.push_back(dcp::out(hired[w]));
  outputs = {{"total_cost", dcp::out(total)}, {"workers", workers}};
}
