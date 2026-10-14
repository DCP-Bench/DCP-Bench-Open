// Kidney exchange: maximize the number of people who receive a kidney, where
// anyone who gives a kidney must also receive one and no person receives more than one.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("num_people");
  const json& compatible = instance.at("compatible");

  // allowed[i][j] = 1 if person i is compatible to donate to person j (lists are 1-based)
  std::vector<std::vector<char>> allowed(n, std::vector<char>(n, 0));
  for (int i = 0; i < n; ++i) {
    for (const auto& p : compatible[i]) {
      allowed[i][p.get<int>() - 1] = 1;
    }
  }

  // transplants[i][j] = 1 if person i donates a kidney to person j
  vec<vec<IntVar*>> tr;
  createVars(tr, n, n, 0, 1, true);
  for (int i = 0; i < n; ++i) {
    for (int j = 0; j < n; ++j) {
      // a person donates only to people it is compatible with
      if (!allowed[i][j]) int_rel(tr[i][j], IRT_EQ, 0);
    }
  }

  // no person donates more than one kidney
  for (int i = 0; i < n; ++i) {
    vec<IntVar*> row;
    for (int j = 0; j < n; ++j) row.push(tr[i][j]);
    int_linear(row, IRT_LE, 1);
  }

  // no person receives more than one kidney
  for (int j = 0; j < n; ++j) {
    vec<IntVar*> col;
    for (int i = 0; i < n; ++i) col.push(tr[i][j]);
    int_linear(col, IRT_LE, 1);
  }

  // anyone who gives a kidney must receive one: donations of i <= receptions of i
  for (int i = 0; i < n; ++i) {
    vec<int> a;
    vec<IntVar*> v;
    for (int j = 0; j < n; ++j) {
      if (j == i) continue;
      a.push(1);
      v.push(tr[i][j]);
    }
    for (int k = 0; k < n; ++k) {
      if (k == i) continue;
      a.push(-1);
      v.push(tr[k][i]);
    }
    int_linear(a, v, IRT_LE, 0);
  }

  // number of people who receive a kidney (one per transplant)
  vec<IntVar*> all;
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) all.push(tr[i][j]);
  IntVar* received = newIntVar(0, n);
  int_linear(all, IRT_EQ, received);

  branch(all, VAR_INORDER, VAL_MAX);
  optimize(received, OPT_MAX);

  json transplants = json::array();
  for (int i = 0; i < n; ++i) {
    json row = json::array();
    for (int j = 0; j < n; ++j) row.push_back(dcp::out(tr[i][j]));
    transplants.push_back(row);
  }
  outputs = {{"transplants", transplants}};
}
