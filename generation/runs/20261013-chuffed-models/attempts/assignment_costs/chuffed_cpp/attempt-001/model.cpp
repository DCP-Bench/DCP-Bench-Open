// Assignment with costs: assign people to tasks so that the total cost is minimized.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<std::vector<int>> cost = instance.at("cost").get<std::vector<std::vector<int>>>();
  int tasks = static_cast<int>(cost.size());
  int people = static_cast<int>(cost[0].size());

  // x[i][j] = 1 if task i is assigned to person j
  vec<vec<IntVar*>> x;
  createVars(x, tasks, people, 0, 1, true);

  // each task must be assigned to exactly one person
  for (int i = 0; i < tasks; ++i) {
    int_linear(x[i], IRT_EQ, 1);
  }

  // it is not necessary to assign all people to a task, but a person takes at most one task
  vec<vec<IntVar*>> by_person;
  transpose(x, by_person);
  for (int j = 0; j < people; ++j) {
    int_linear(by_person[j], IRT_LE, 1);
  }

  // total cost is the sum of the costs of the chosen assignments (bounded by the sum of the row maxima)
  vec<int> coefs;
  vec<IntVar*> cells;
  int bound = 0;
  for (int i = 0; i < tasks; ++i) {
    int row_max = 0;
    for (int j = 0; j < people; ++j) {
      coefs.push(cost[i][j]);
      cells.push(x[i][j]);
      if (cost[i][j] > row_max) row_max = cost[i][j];
    }
    bound += row_max;
  }
  IntVar* total_cost = newIntVar(0, bound);
  int_linear(coefs, cells, IRT_EQ, total_cost);

  // minimize the total cost
  branch(cells, VAR_INORDER, VAL_MIN);
  optimize(total_cost, OPT_MIN);

  json rows = json::array();
  for (int i = 0; i < tasks; ++i) {
    json row = json::array();
    for (int j = 0; j < people; ++j) row.push_back(dcp::out(x[i][j]));
    rows.push_back(row);
  }
  outputs = {{"x", rows}};
}
