// Kidney exchange: maximize the number of people who receive a kidney, where
// anyone who gives a kidney must also receive one and no person receives more than one.
// Each person i gives to at most one person and receives from at most one person.
// Model: succ[i] is the person that i donates to, with succ[i] = i meaning i does not
// take part. Every donor must receive, so the donations form a permutation: the
// successors are all different, and the cycles of the permutation are the exchanges.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("num_people");
  const json& compatible = instance.at("compatible");

  // allowed[i][j] = 1 if person i can donate to person j (lists are 1-based in the data)
  std::vector<std::vector<char>> allowed(n, std::vector<char>(n, 0));
  for (int i = 0; i < n; ++i) {
    for (const auto& p : compatible[i]) {
      allowed[i][p.get<int>() - 1] = 1;
    }
  }

  // succ[i] = the person that i donates to; i itself when i does not take part
  vec<IntVar*> succ;
  createVars(succ, n, 0, n - 1);
  for (int i = 0; i < n; ++i) {
    for (int j = 0; j < n; ++j) {
      // a person donates only to people it is compatible with, or to nobody
      if (j != i && !allowed[i][j]) int_rel(succ[i], IRT_NE, j);
    }
  }

  // nobody receives more than one kidney, and the donations form disjoint cycles
  all_different(succ, CL_DOM);

  // transplants[i][j] = 1 if person i donates a kidney to person j
  vec<vec<IntVar*>> tr;
  tr.growTo(n);
  for (int i = 0; i < n; ++i) {
    for (int j = 0; j < n; ++j) {
      if (j == i || !allowed[i][j]) {
        tr[i].push(getConstant(0));
        continue;
      }
      BoolView r = newBoolVar();
      int_rel_reif(succ[i], IRT_EQ, j, r);
      IntVar* t = newIntVar(0, 1);
      bool2int(r, t);
      tr[i].push(t);
    }
  }

  // number of people who receive a kidney (one per transplant)
  vec<IntVar*> all;
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j)
      if (j != i && allowed[i][j]) all.push(tr[i][j]);
  IntVar* received = newIntVar(0, n);
  int_linear(all, IRT_EQ, received);

  // decide the transplants first, then the successors
  branch(succ, VAR_SIZE_MIN, VAL_MAX);
  optimize(received, OPT_MAX);

  json transplants = json::array();
  for (int i = 0; i < n; ++i) {
    json row = json::array();
    for (int j = 0; j < n; ++j) row.push_back(dcp::out(tr[i][j]));
    transplants.push_back(row);
  }
  outputs = {{"transplants", transplants}};
}
