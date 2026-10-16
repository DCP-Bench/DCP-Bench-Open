// Farmer and cows: a farmer has num_cows cows, cow c (1..num_cows) gives c units of milk,
// and must give each son a given number of cows so that every son gets the same milk.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int N = instance.at("num_cows");
  int S = instance.at("num_sons");
  std::vector<int> per = instance.at("cows_per_son").get<std::vector<int>>();

  // every son gets the same milk: an equal share of the total milk of all cows
  int total_milk = N * (N + 1) / 2;
  int milk_per_son = total_milk / S;

  // x[c][s] = 1 if cow c goes to son s, as a 0..1 integer and as a Boolean
  vec<vec<IntVar*>> x;
  createVars(x, N, S, 0, 1, true);
  vec<vec<BoolView>> xb;
  xb.growTo(N);
  for (int c = 0; c < N; ++c) {
    for (int s = 0; s < S; ++s) {
      BoolView b = newBoolVar();
      bool2int(b, x[c][s]);
      xb[c].push(b);
    }
  }

  // every cow goes to exactly one son
  for (int c = 0; c < N; ++c) {
    vec<IntVar*> row;
    for (int s = 0; s < S; ++s) row.push(x[c][s]);
    int_linear(row, IRT_EQ, 1);
  }

  // each son gets the number of cows given by the distribution
  for (int s = 0; s < S; ++s) {
    vec<IntVar*> col;
    for (int c = 0; c < N; ++c) col.push(x[c][s]);
    int_linear(col, IRT_EQ, per[s]);
  }

  // the milk of a son is the sum of the numbers of its cows, and equals milk_per_son
  for (int s = 0; s < S; ++s) {
    vec<int> milk;
    vec<IntVar*> col;
    for (int c = 0; c < N; ++c) {
      milk.push(c + 1);
      col.push(x[c][s]);
    }
    int_linear(milk, col, IRT_EQ, milk_per_son);
  }

  // sons with the same number of cows are interchangeable: the first cow of son s comes
  // before the first cow of son s+1 (value precedence, keeps one labelling per solution)
  for (int s = 1; s < S; ++s) {
    if (per[s] != per[s - 1]) continue;
    for (int c = 0; c < N; ++c) {
      vec<BoolView> pos, neg;
      for (int e = 0; e < c; ++e) pos.push(xb[e][s - 1]);
      neg.push(xb[c][s]);
      bool_clause(pos, neg);
    }
  }

  // son index of each cow
  vec<IntVar*> son;
  for (int c = 0; c < N; ++c) {
    IntVar* sc = newIntVar(0, S - 1);
    vec<int> idx;
    vec<IntVar*> row;
    for (int s = 0; s < S; ++s) {
      idx.push(s);
      row.push(x[c][s]);
    }
    int_linear(idx, row, IRT_EQ, sc);
    son.push(sc);
  }

  // fill one son at a time, taking the cows with the largest milk first and
  // trying to give a cow to the son (1) before leaving it out
  vec<IntVar*> son_major;
  for (int s = 0; s < S; ++s)
    for (int c = N - 1; c >= 0; --c) son_major.push(x[c][s]);
  branch(son_major, VAR_INORDER, VAL_MAX);

  json assign = json::array();
  for (int c = 0; c < N; ++c) assign.push_back(dcp::out(son[c]));
  outputs = {{"cow_assignments", assign}};
}
