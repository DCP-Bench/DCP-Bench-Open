// Aircraft assignment: assign aircraft of each type to routes so that passenger demand is met
// within the availability of each type, at minimum total operational cost.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<int> availability = instance.at("availability").get<std::vector<int>>();
  std::vector<int> demand = instance.at("demand").get<std::vector<int>>();
  std::vector<std::vector<int>> capabilities = instance.at("capabilities").get<std::vector<std::vector<int>>>();
  std::vector<std::vector<int>> costs = instance.at("costs").get<std::vector<std::vector<int>>>();
  int types = static_cast<int>(availability.size());
  int routes = static_cast<int>(demand.size());

  // allocation[i][j] = number of aircraft of type i assigned to route j
  // (at most availability[i], since a type cannot be used more often than it is available)
  vec<vec<IntVar*>> allocation;
  for (int i = 0; i < types; ++i) {
    allocation.push();
    createVars(allocation.last(), routes, 0, availability[i]);
  }

  // each aircraft type has a limited number of available units
  for (int i = 0; i < types; ++i) {
    int_linear(allocation[i], IRT_LE, availability[i]);
  }

  // the passenger demand of each route must be satisfied
  for (int j = 0; j < routes; ++j) {
    vec<int> cap;
    vec<IntVar*> col;
    for (int i = 0; i < types; ++i) {
      cap.push(capabilities[i][j]);
      col.push(allocation[i][j]);
    }
    int_linear(cap, col, IRT_GE, demand[j]);
  }

  // total operational cost; its upper bound is every available aircraft flying its most expensive route
  vec<int> cost;
  vec<IntVar*> all;
  int bound = 0;
  for (int i = 0; i < types; ++i) {
    int mx = 0;
    for (int j = 0; j < routes; ++j) {
      cost.push(costs[i][j]);
      all.push(allocation[i][j]);
      if (costs[i][j] > mx) mx = costs[i][j];
    }
    bound += availability[i] * mx;
  }
  IntVar* total = newIntVar(0, bound);
  int_linear(cost, all, IRT_EQ, total);

  // minimize the overall cost
  branch(all, VAR_INORDER, VAL_MIN);
  optimize(total, OPT_MIN);

  json alloc = json::array();
  for (int i = 0; i < types; ++i) {
    json row = json::array();
    for (int j = 0; j < routes; ++j) row.push_back(dcp::out(allocation[i][j]));
    alloc.push_back(row);
  }
  outputs = {{"allocation", alloc}};
}
