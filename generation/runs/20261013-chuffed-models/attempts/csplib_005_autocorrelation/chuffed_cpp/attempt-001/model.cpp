// Binary autocorrelation (periodic): choose a sequence of n bits, each +1 or -1, that minimizes
// the sum of the squares of its periodic autocorrelations.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");

  // s[i] is bit i of the sequence, +1 or -1 (the bound is -1..1 and 0 is excluded below)
  vec<IntVar*> s;
  createVars(s, n, -1, 1, true);
  for (int i = 0; i < n; ++i) int_rel(s[i], IRT_NE, 0);

  // the sequence is symmetric under negating every bit, so fix the first bit to +1
  int_rel(s[0], IRT_EQ, 1);

  // E accumulates the sum over k = 1 .. n-1 of the squared periodic autocorrelation C_k
  vec<int> ones_sq;
  vec<IntVar*> squares;
  for (int k = 1; k < n; ++k) {
    // products[i] = s[i] * s[(i + k) mod n], the terms of C_k
    vec<IntVar*> products;
    for (int i = 0; i < n; ++i) {
      IntVar* p = newIntVar(-1, 1);
      int_times(s[i], s[(i + k) % n], p);
      products.push(p);
    }

    // C_k is the sum of the products over all n positions (periodic boundary)
    vec<int> ones;
    for (int i = 0; i < n; ++i) ones.push(1);
    IntVar* ck = newIntVar(-n, n);
    int_linear(ones, products, IRT_EQ, ck);

    // the squared autocorrelation C_k^2
    IntVar* sq = newIntVar(0, n * n);
    int_times(ck, ck, sq);
    squares.push(sq);
    ones_sq.push(1);
  }

  // the energy E is the sum of the squared autocorrelations, to be minimized
  IntVar* energy = newIntVar(0, n * n * n);
  int_linear(ones_sq, squares, IRT_EQ, energy);

  // decide the bits in order
  branch(s, VAR_INORDER, VAL_MIN);
  optimize(energy, OPT_MIN);

  json seq = json::array();
  for (int i = 0; i < n; ++i) seq.push_back(dcp::out(s[i]));
  outputs = {{"sequence", seq}};
}
