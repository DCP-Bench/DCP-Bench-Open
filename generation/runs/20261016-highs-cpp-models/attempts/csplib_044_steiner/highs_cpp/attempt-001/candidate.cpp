// Ternary Steiner problem of order n (csplib 044): find n(n-1)/6 triples of distinct
// elements from 1..n such that any two triples have at most one common element.
// Output "sets" is a [n(n-1)/6][n] boolean matrix: entry [i][j] is true when element j+1
// is part of triple i.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int n = instance.at("n").get<int>();
  const int triples = n * (n - 1) / 6;

  // x[t][e] = 1 when element e (0-based) is in triple t.
  std::vector<std::vector<dcp::Lin>> x(triples, std::vector<dcp::Lin>(n));
  for (int t = 0; t < triples; ++t)
    for (int e = 0; e < n; ++e) x[t][e] = dcp::new_var(h, 0, 1);

  // each triple contains exactly three distinct elements
  for (int t = 0; t < triples; ++t) {
    dcp::Lin size;
    for (int e = 0; e < n; ++e) size = size + x[t][e];
    dcp::add_row(h, size, 3, 3);
  }

  // any two triples have at most one common element: each pair of elements lies in at most one triple
  for (int i = 0; i < n; ++i) {
    for (int j = i + 1; j < n; ++j) {
      dcp::Lin pair_count;
      for (int t = 0; t < triples; ++t) {
        // both is 1 when triple t contains elements i and j (both >= x[t][i] + x[t][j] - 1)
        dcp::Lin both = dcp::new_var(h, 0, 1);
        dcp::add_row(h, both - x[t][i] - x[t][j], -1, kHighsInf);
        pair_count = pair_count + both;
      }
      // at most one triple contains the pair {i, j}
      dcp::add_row(h, pair_count, -kHighsInf, 1);
    }
  }

  out.add("sets", x);
}
