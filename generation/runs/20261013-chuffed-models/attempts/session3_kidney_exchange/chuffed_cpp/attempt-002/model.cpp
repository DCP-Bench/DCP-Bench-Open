// Kidney exchange: n people on a waiting list; compatible[i] lists the people that person i can donate to.
// transplants[i][j] = 1 if person i donates a kidney to person j; the objective is the number of people who receive one.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("num_people");
  // the compatibility lists use 1-based person numbers; the output matrix is 0-based
  std::vector<std::vector<int>> compatible = instance.at("compatible").get<std::vector<std::vector<int>>>();

  // transplants[i][j] is 1 if person i donates to person j (0-based indices)
  vec<vec<IntVar*>> tx;
  createVars(tx, n, n, 0, 1, true);

  // a person can only donate to a compatible person; all other pairs stay 0
  for (int i = 0; i < n; ++i) {
    for (int j = 0; j < n; ++j) {
      bool ok = false;
      for (int p : compatible[i]) {
        if (p - 1 == j) ok = true;
      }
      if (!ok) int_rel(tx[i][j], IRT_EQ, 0);
    }
  }

  // no person receives more than one kidney
  for (int j = 0; j < n; ++j) {
    vec<IntVar*> received;
    for (int i = 0; i < n; ++i) received.push(tx[i][j]);
    int_linear(received, IRT_LE, 1);
  }

  // anyone who gives a kidney must receive one: if person i donates at all, i receives one
  // (out_i <= n * in_i, and in_i is 0 or 1)
  for (int i = 0; i < n; ++i) {
    vec<int> sign;
    vec<IntVar*> vars;
    for (int j = 0; j < n; ++j) {
      sign.push(1);
      vars.push(tx[i][j]);
    }
    for (int j = 0; j < n; ++j) {
      sign.push(-n);
      vars.push(tx[j][i]);
    }
    int_linear(sign, vars, IRT_LE, 0);
  }

  // total is the number of people who receive a kidney
  vec<IntVar*> all;
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) all.push(tx[i][j]);
  IntVar* total = newIntVar(0, n);
  int_linear(all, IRT_EQ, total);

  // the donation matrix is the decision; search in reading order
  branch(all, VAR_INORDER, VAL_MAX);
  optimize(total, OPT_MAX);

  json rows = json::array();
  for (int i = 0; i < n; ++i) {
    json row = json::array();
    for (int j = 0; j < n; ++j) row.push_back(dcp::out(tx[i][j]));
    rows.push_back(row);
  }
  outputs = {{"transplants", rows}};
}
