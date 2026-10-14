// Kidney exchange: people on a waiting list donate kidneys to each other. Person i can donate to the people in
// compatible[i]. Anyone who gives a kidney must receive one, and nobody receives more than one kidney.
// Maximise the number of people who receive a kidney.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("num_people");
  auto compatible = instance.at("compatible").get<std::vector<std::vector<int>>>();

  // allowed[i][j] is true when person i can donate to person j (1-based ids in the instance)
  std::vector<std::vector<char>> allowed(n, std::vector<char>(n, 0));
  for (int i = 0; i < n; ++i)
    for (int j : compatible[i])
      if (j >= 1 && j <= n && j - 1 != i) allowed[i][j - 1] = 1;

  // gift[i][j] is true when person i donates a kidney to person j
  std::vector<std::vector<BoolView>> gift(n, std::vector<BoolView>(n));
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j)
      if (allowed[i][j]) gift[i][j] = newBoolVar();

  // each person donates at most one kidney
  for (int i = 0; i < n; ++i) {
    vec<BoolView> out;
    for (int j = 0; j < n; ++j)
      if (allowed[i][j]) out.push(gift[i][j]);
    if (out.size() > 0) bool_linear(out, IRT_LE, getConstant(1));
  }

  // each person receives at most one kidney
  for (int j = 0; j < n; ++j) {
    vec<BoolView> in;
    for (int i = 0; i < n; ++i)
      if (allowed[i][j]) in.push(gift[i][j]);
    if (in.size() > 0) bool_linear(in, IRT_LE, getConstant(1));
  }

  // anyone who gives a kidney must receive one: donates(i) implies receives(i)
  for (int i = 0; i < n; ++i) {
    vec<BoolView> out, in;
    for (int j = 0; j < n; ++j) {
      if (allowed[i][j]) out.push(gift[i][j]);
      if (allowed[j][i]) in.push(gift[j][i]);
    }
    if (out.size() == 0) continue;  // person i cannot donate, nothing to require
    if (in.size() == 0) {  // nobody can give to i, so i cannot donate
      for (int j = 0; j < n; ++j)
        if (allowed[i][j]) {
          vec<BoolView> none, neg;
          neg.push(gift[i][j]);
          bool_clause(none, neg);  // gift[i][j] must be false
        }
      continue;
    }
    BoolView d = newBoolVar(), r = newBoolVar();
    array_bool_or(out, d);
    array_bool_or(in, r);
    vec<BoolView> pos, neg;
    pos.push(r);
    neg.push(d);
    bool_clause(pos, neg);
  }

  // the number of people who receive a kidney is the number of gifts
  vec<BoolView> all;
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j)
      if (allowed[i][j]) all.push(gift[i][j]);
  IntVar* received = newIntVar(0, n);
  if (all.size() > 0) bool_linear(all, IRT_EQ, received);
  else int_rel(received, IRT_EQ, 0);

  // gift01 holds the 0/1 transplant matrix, row-major
  vec<IntVar*> gift01;
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) {
      IntVar* g = newIntVar(0, 1);
      if (allowed[i][j]) bool2int(gift[i][j], g);
      else int_rel(g, IRT_EQ, 0);
      gift01.push(g);
    }
  vec<IntVar*> objv;
  objv.push(received);
  branch(objv, VAR_INORDER, VAL_MAX);
  branch(gift01, VAR_INORDER, VAL_MAX);
  optimize(received, OPT_MAX);

  // transplants[i][j] is 1 when person i donates to person j
  json rows = json::array();
  for (int i = 0; i < n; ++i) {
    json row = json::array();
    for (int j = 0; j < n; ++j) row.push_back(dcp::out(gift01[i * n + j]));
    rows.push_back(row);
  }
  outputs = {{"transplants", rows}};
}
