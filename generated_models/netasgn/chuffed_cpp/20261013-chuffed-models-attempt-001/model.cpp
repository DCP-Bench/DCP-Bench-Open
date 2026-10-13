// Project assignment: assign hours from people to projects at minimum total cost.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<int> supply = instance.at("supply").get<std::vector<int>>();
  std::vector<int> demand = instance.at("demand").get<std::vector<int>>();
  std::vector<std::vector<int>> cost = instance.at("cost").get<std::vector<std::vector<int>>>();
  std::vector<std::vector<int>> limit = instance.at("limit").get<std::vector<std::vector<int>>>();
  int np = static_cast<int>(supply.size());
  int nj = static_cast<int>(demand.size());

  // assign[i][j] is the number of hours person i works on project j, at most limit[i][j]
  vec<vec<IntVar*>> assign(np);
  for (int i = 0; i < np; ++i)
    for (int j = 0; j < nj; ++j) assign[i].push(newIntVar(0, limit[i][j]));

  // the total number of hours assigned from each person equals the person's supply
  for (int i = 0; i < np; ++i) int_linear(assign[i], IRT_EQ, supply[i]);

  // the total number of hours assigned to each project equals its demand
  for (int j = 0; j < nj; ++j) {
    vec<IntVar*> col;
    for (int i = 0; i < np; ++i) col.push(assign[i][j]);
    int_linear(col, IRT_EQ, demand[j]);
  }

  // total_cost is the cost per hour times the hours, summed over all assignments
  vec<int> coef;
  vec<IntVar*> all;
  int max_cost = 0;
  for (int i = 0; i < np; ++i)
    for (int j = 0; j < nj; ++j) {
      coef.push(cost[i][j]);
      all.push(assign[i][j]);
      max_cost += cost[i][j] * limit[i][j];
    }
  IntVar* total_cost = newIntVar(0, max_cost);
  int_linear(coef, all, IRT_EQ, total_cost);

  // minimize the total cost
  branch(all, VAR_INORDER, VAL_MIN);
  optimize(total_cost, OPT_MIN);

  json rows = json::array();
  for (int i = 0; i < np; ++i) {
    json row = json::array();
    for (int j = 0; j < nj; ++j) row.push_back(dcp::out(assign[i][j]));
    rows.push_back(row);
  }
  outputs = {{"assign", rows}, {"total_cost", dcp::out(total_cost)}};
}
