// Farmer and cows: give each cow (numbered 1..num_cows) to one of the sons so that each son receives the given number of cows and the same total milk.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int ncows = instance.at("num_cows");
  int nsons = instance.at("num_sons");
  std::vector<int> per_son = instance.at("cows_per_son").get<std::vector<int>>();  // number of cows each son gets

  // son[c] = son that receives cow c+1
  vec<IntVar*> son;
  createVars(son, ncows, 0, nsons - 1);

  // to[c][s] = 1 if cow c+1 goes to son s
  vec<vec<BoolView>> to;
  createVars(to, ncows, nsons);
  for (int c = 0; c < ncows; ++c) {
    for (int s = 0; s < nsons; ++s) int_rel_reif(son[c], IRT_EQ, s, to[c][s]);
  }

  // each son gets the number of cows given by the distribution
  for (int s = 0; s < nsons; ++s) {
    vec<BoolView> got;
    for (int c = 0; c < ncows; ++c) got.push(to[c][s]);
    bool_linear(got, IRT_EQ, getConstant(per_son[s]));
  }

  // the milk of cow c+1 is c+1; the total is the sum 1..ncows, and every son gets an equal share of it
  int total = ncows * (ncows + 1) / 2;
  int share = total / nsons;
  for (int s = 0; s < nsons; ++s) {
    // the milk of the cows given to son s
    vec<IntVar*> bits;
    vec<int> milk;
    for (int c = 0; c < ncows; ++c) {
      IntVar* bit = newIntVar(0, 1);
      bool2int(to[c][s], bit);
      bits.push(bit);
      milk.push(c + 1);
    }
    int_linear(milk, bits, IRT_EQ, share);
  }

  // symmetry breaking: when all sons get the same number of cows they are interchangeable, so the
  // sons are numbered in the order of their first cow (son[c] is at most one more than the largest son before it)
  bool same = true;
  for (int s = 1; s < nsons; ++s) same = same && per_son[s] == per_son[0];
  if (same && ncows > 0) {
    int_rel(son[0], IRT_EQ, 0);
    vec<IntVar*> prefix;
    prefix.push(son[0]);
    for (int c = 1; c < ncows; ++c) {
      // largest son number among the cows before cow c+1
      IntVar* top = newIntVar(0, nsons - 1);
      vec<IntVar*> before;
      for (int k = 0; k < c; ++k) before.push(son[k]);
      maximum(before, top);
      // son of cow c+1 is at most top + 1
      vec<int> one_one;
      one_one.push(1);
      one_one.push(-1);
      vec<IntVar*> pair;
      pair.push(son[c]);
      pair.push(top);
      int_linear(one_one, pair, IRT_LE, 1);
    }
  }

  // branch on the cows in order
  branch(son, VAR_INORDER, VAL_MIN);

  json assign = json::array();
  for (int c = 0; c < ncows; ++c) assign.push_back(dcp::out(son[c]));
  outputs = {{"cow_assignments", assign}};
}
