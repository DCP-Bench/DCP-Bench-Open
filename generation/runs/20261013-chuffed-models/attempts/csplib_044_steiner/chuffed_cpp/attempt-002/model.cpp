// Ternary Steiner system of order n: choose n(n-1)/6 triples of distinct elements from 1..n so that
// any two triples share at most one element.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");

  // the number of triples in the system is n(n-1)/6 (the problem requires n mod 6 = 1 or 3)
  int triples = n * (n - 1) / 6;

  // in[t][j] is true when element j+1 belongs to triple t (columns are elements 1..n)
  vec<vec<BoolView>> in;
  createVars(in, triples, n);

  // every triple has exactly three distinct elements
  for (int t = 0; t < triples; ++t) {
    bool_linear(in[t], IRT_EQ, getConstant(3));
  }

  // two triples share at most one element exactly when no pair of elements lies in two triples.
  // Each pair {a, b} is in at most one triple.
  // Each triple covers three pairs, so the triples cover n(n-1)/2 pairs in total, which is every pair
  // once; so every pair lies in exactly one triple (implied, and it prunes the search).
  for (int a = 0; a < n; ++a) {
    for (int b = a + 1; b < n; ++b) {
      // covers[t] is true when triple t contains both elements a+1 and b+1
      vec<BoolView> covers;
      for (int t = 0; t < triples; ++t) {
        BoolView both = newBoolVar();
        vec<BoolView> pair;
        pair.push(in[t][a]);
        pair.push(in[t][b]);
        array_bool_and(pair, both);
        covers.push(both);
      }

      // the pair {a+1, b+1} lies in exactly one triple
      bool_linear(covers, IRT_EQ, getConstant(1));
    }
  }

  // export each membership flag as a 0/1 integer; the flags are the decision variables
  vec<IntVar*> flags;
  for (int t = 0; t < triples; ++t) {
    for (int j = 0; j < n; ++j) {
      IntVar* e = newIntVar(0, 1);
      bool2int(in[t][j], e);
      flags.push(e);
    }
  }
  branch(flags, VAR_INORDER, VAL_MIN);

  json rows = json::array();
  for (int t = 0; t < triples; ++t) {
    json row = json::array();
    for (int j = 0; j < n; ++j) row.push_back(dcp::out(flags[t * n + j]));
    rows.push_back(row);
  }
  outputs = {{"sets", rows}};
}
