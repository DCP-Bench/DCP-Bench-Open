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
    // each triple consists of three elements
    bool_linear(in[t], IRT_EQ, getConstant(3));
  }

  // any two distinct triples have at most one element in common
  for (int t = 0; t < triples; ++t) {
    for (int u = t + 1; u < triples; ++u) {
      // shared[j] is true when element j+1 is in both triple t and triple u
      vec<BoolView> shared;
      for (int j = 0; j < n; ++j) {
        BoolView both = newBoolVar();
        vec<BoolView> pair;
        pair.push(in[t][j]);
        pair.push(in[u][j]);
        array_bool_and(pair, both);
        shared.push(both);
      }

      // at most one common element between the two triples
      bool_linear(shared, IRT_LE, getConstant(1));
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
