// Appointment scheduling: assign each of the people to one interview slot, respecting who is free when.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // m[i][j] = 1 if person i is free in slot j (rows are people, columns are slots)
  std::vector<std::vector<int>> m = instance.at("m").get<std::vector<std::vector<int>>>();
  int n = static_cast<int>(m.size());

  // x[i][j] = 1 if person i is assigned to slot j
  vec<vec<IntVar*>> x;
  createVars(x, n, n, 0, 1, true);

  // a person can only be assigned to a slot in which that person is free
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j)
      if (m[i][j] == 0) int_rel(x[i][j], IRT_EQ, 0);

  // every person gets exactly one slot
  for (int i = 0; i < n; ++i) {
    vec<IntVar*> row;
    for (int j = 0; j < n; ++j) row.push(x[i][j]);
    int_linear(row, IRT_EQ, 1);
  }

  // every slot gets exactly one person
  for (int j = 0; j < n; ++j) {
    vec<IntVar*> col;
    for (int i = 0; i < n; ++i) col.push(x[i][j]);
    int_linear(col, IRT_EQ, 1);
  }

  vec<IntVar*> flat;
  flatten(x, flat);
  branch(flat, VAR_INORDER, VAL_MIN);

  json rows = json::array();
  for (int i = 0; i < n; ++i) {
    json r = json::array();
    for (int j = 0; j < n; ++j) r.push_back(dcp::out(x[i][j]));
    rows.push_back(r);
  }
  outputs = {{"x", rows}};
}
