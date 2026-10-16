// Car selection: assign participants to cars they are interested in, at most one car per
// participant and one participant per car, maximizing the number of assignments.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<std::vector<int>> possible =
      instance.at("possible_assignments").get<std::vector<std::vector<int>>>();
  int n = static_cast<int>(possible.size());     // participants
  int m = n > 0 ? static_cast<int>(possible[0].size()) : 0;  // cars

  // assignments[i][j] = 1 if participant i is assigned to car j
  vec<vec<IntVar*>> assignments;
  createVars(assignments, n, m, 0, 1, true);

  // a participant can only be assigned to a car they are interested in
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < m; ++j)
      if (!possible[i][j]) int_rel(assignments[i][j], IRT_EQ, 0);

  // each participant is assigned to at most one car
  for (int i = 0; i < n; ++i) int_linear(assignments[i], IRT_LE, 1);

  // each car is assigned to at most one participant
  vec<vec<IntVar*>> by_car;
  transpose(assignments, by_car);
  for (int j = 0; j < m; ++j) int_linear(by_car[j], IRT_LE, 1);

  // maximize the total number of assignments
  vec<IntVar*> flat;
  flatten(assignments, flat);
  IntVar* total = newIntVar(0, n < m ? n : m);
  int_linear(flat, IRT_EQ, total);

  branch(flat, VAR_INORDER, VAL_MAX);
  optimize(total, OPT_MAX);

  json rows = json::array();
  for (int i = 0; i < n; ++i) {
    json row = json::array();
    for (int j = 0; j < m; ++j) row.push_back(dcp::out(assignments[i][j]));
    rows.push_back(row);
  }
  outputs = {{"assignments", rows}};
}
