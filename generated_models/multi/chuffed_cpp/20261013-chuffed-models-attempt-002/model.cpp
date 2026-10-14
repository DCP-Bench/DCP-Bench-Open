// Multi-commodity transportation: ship products from origins to destinations at minimum
// total shipping cost, within supplies, demands and per-lane limits.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  auto supply = instance.at("supply").get<std::vector<std::vector<int>>>();  // [origin][product]
  auto demand = instance.at("demand").get<std::vector<std::vector<int>>>();  // [dest][product]
  auto limit = instance.at("limit").get<std::vector<std::vector<int>>>();    // [origin][dest]
  auto cost = instance.at("cost").get<std::vector<std::vector<std::vector<int>>>>();  // [o][d][p]
  int O = static_cast<int>(supply.size());
  int D = static_cast<int>(demand.size());
  int P = static_cast<int>(supply[0].size());

  // ship[i][j][p] = units of product p shipped from origin i to destination j
  std::vector<std::vector<std::vector<IntVar*>>> ship(
      O, std::vector<std::vector<IntVar*>>(D, std::vector<IntVar*>(P)));
  for (int i = 0; i < O; ++i)
    for (int j = 0; j < D; ++j)
      for (int p = 0; p < P; ++p) {
        int ub = std::min(supply[i][p], demand[j][p]);  // never more than either side
        ship[i][j][p] = newIntVar(0, ub);
      }

  // each origin ships at most its supply of each product
  for (int i = 0; i < O; ++i)
    for (int p = 0; p < P; ++p) {
      vec<IntVar*> vs;
      for (int j = 0; j < D; ++j) vs.push(ship[i][j][p]);
      int_linear(vs, IRT_LE, supply[i][p]);
    }

  // each destination receives exactly its demand of each product
  for (int j = 0; j < D; ++j)
    for (int p = 0; p < P; ++p) {
      vec<IntVar*> vs;
      for (int i = 0; i < O; ++i) vs.push(ship[i][j][p]);
      int_linear(vs, IRT_EQ, demand[j][p]);
    }

  // the total shipped over each origin-destination lane (all products) is within its limit
  for (int i = 0; i < O; ++i)
    for (int j = 0; j < D; ++j) {
      vec<IntVar*> vs;
      for (int p = 0; p < P; ++p) vs.push(ship[i][j][p]);
      int_linear(vs, IRT_LE, limit[i][j]);
    }

  // the total cost is the sum of unit shipping costs times the units shipped
  vec<int> co;
  vec<IntVar*> vs;
  int max_cost = 0;
  for (int i = 0; i < O; ++i)
    for (int j = 0; j < D; ++j)
      for (int p = 0; p < P; ++p) {
        co.push(cost[i][j][p]);
        vs.push(ship[i][j][p]);
        max_cost += cost[i][j][p] * std::min(supply[i][p], demand[j][p]);
      }
  IntVar* total_cost = newIntVar(0, max_cost);
  int_linear(co, vs, IRT_EQ, total_cost);

  // minimize the total shipping cost
  branch(vs, VAR_INORDER, VAL_MIN);
  optimize(total_cost, OPT_MIN);

  outputs = {{"total_cost", dcp::out(total_cost)}};
}
