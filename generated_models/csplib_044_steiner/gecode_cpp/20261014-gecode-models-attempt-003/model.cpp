#include "dcp.h"

// Ternary Steiner problem of order n: find n(n-1)/6 triples of distinct elements
// of {1..n} such that any two triples have at most one common element.
// Elements are 0-based inside the model. Output "sets": one row per triple, one
// column per element, true if the element is in the triple.
class Steiner : public dcp::Space {
 protected:
  int n;          // number of elements
  int T;          // number of triples, n(n-1)/6
  BoolVarArray x; // x[t*n + j]: element j is in triple t

 public:
  explicit Steiner(const json& instance) {
    n = instance.at("n").get<int>();
    T = n * (n - 1) / 6;   // the instance gives n, n mod 6 must be 1 or 3
    x = BoolVarArray(*this, T * n, 0, 1);

    // each triple consists of exactly three distinct elements
    for (int t = 0; t < T; ++t) {
      BoolVarArgs row;
      for (int j = 0; j < n; ++j) row << x[t * n + j];
      linear(*this, row, IRT_EQ, 3);
    }

    // any two triples have at most one common element
    for (int t1 = 0; t1 < T; ++t1)
      for (int t2 = t1 + 1; t2 < T; ++t2) {
        BoolVarArgs both;
        for (int j = 0; j < n; ++j) both << expr(*this, x[t1 * n + j] && x[t2 * n + j]);
        linear(*this, both, IRT_LQ, 1);
      }

    // redundant (implied by counting): every pair of elements lies in exactly one triple,
    // since 3T = n(n-1)/2 and each pair is covered at most once
    for (int a = 0; a < n; ++a)
      for (int b = a + 1; b < n; ++b) {
        BoolVarArgs cover;
        for (int t = 0; t < T; ++t) cover << expr(*this, x[t * n + a] && x[t * n + b]);
        linear(*this, cover, IRT_EQ, 1);
      }

    // redundant (implied by counting): every element lies in (n-1)/2 triples
    for (int j = 0; j < n; ++j) {
      BoolVarArgs column;
      for (int t = 0; t < T; ++t) column << x[t * n + j];
      linear(*this, column, IRT_EQ, (n - 1) / 2);
    }

    // the triples form a set, so their order is free: rows in lexicographic order
    // (symmetry breaking; two triples are never equal, so the order is strict)
    for (int t = 0; t + 1 < T; ++t) {
      BoolVarArgs rowA, rowB;
      for (int j = 0; j < n; ++j) {
        rowA << x[t * n + j];
        rowB << x[(t + 1) * n + j];
      }
      rel(*this, rowA, IRT_LQ, rowB);
    }

    // branch on the Booleans by activity, with Luby restarts: a fixed row-by-row order thrashes on larger orders
    // (the pair and column sums then force the rest)
    branch(*this, x, BOOL_VAR_AFC_MAX(0.99), BOOL_VAL_MAX());
    restarts(100);

    std::vector<BoolVarArgs> sets(T);
    for (int t = 0; t < T; ++t)
      for (int j = 0; j < n; ++j) sets[t] << x[t * n + j];
    output("sets", sets);
  }

  Steiner(Steiner& s) : dcp::Space(s), n(s.n), T(s.T) { x.update(*this, s.x); }
  Gecode::Space* copy() override { return new Steiner(*this); }
};

DCP_MODEL(Steiner)
