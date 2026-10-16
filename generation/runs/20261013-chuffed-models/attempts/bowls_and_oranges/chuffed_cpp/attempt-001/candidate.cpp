// Bowls and oranges: place m oranges in n bowls standing in a line at 1 metre spacing,
// at most one orange per bowl, so that no three oranges A, B, C have dist(A,B) = dist(B,C).
// Bowls are numbered 1 to n along the line.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");
  int m = instance.at("m");

  // x[i] is the bowl of the i-th orange, numbered in ascending order
  vec<IntVar*> x;
  createVars(x, m, 1, n);

  // the oranges sit in distinct bowls, listed in ascending order
  for (int i = 0; i + 1 < m; ++i) int_rel(x[i], IRT_LT, x[i + 1]);

  // occ[k-1] is true when bowl k holds an orange: some x[i] equals k
  vec<BoolView> occ;
  createVars(occ, n);
  for (int k = 1; k <= n; ++k) {
    vec<BoolView> hits;
    for (int i = 0; i < m; ++i) {
      BoolView b = newBoolVar();
      int_rel_reif(x[i], IRT_EQ, k, b);
      hits.push(b);
    }
    array_bool_or(hits, occ[k - 1]);
  }

  // no three bowls at positions a, a+d, a+2d (equal spacing d) may all hold an orange
  for (int a = 0; a < n; ++a) {
    for (int d = 1; a + 2 * d < n; ++d) {
      vec<BoolView> pos, neg;
      neg.push(occ[a]);
      neg.push(occ[a + d]);
      neg.push(occ[a + 2 * d]);
      bool_clause(pos, neg);
    }
  }

  // the oranges' bowls are the decision variables
  branch(x, VAR_INORDER, VAL_MIN);

  json bowls = json::array();
  for (int i = 0; i < m; ++i) bowls.push_back(dcp::out(x[i]));
  outputs = {{"x", bowls}};
}
