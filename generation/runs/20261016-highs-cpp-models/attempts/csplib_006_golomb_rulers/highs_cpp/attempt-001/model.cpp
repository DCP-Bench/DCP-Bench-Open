// csplib_006_golomb_rulers: a Golomb ruler with m marks 0 = a_1 < ... < a_m whose
// pairwise differences are all distinct; minimise the length a_m.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int m = instance.at("size").get<int>();

  // Upper bound on every mark. Placing each new mark at the last mark plus the
  // largest difference so far plus one gives a valid ruler of length 2^m - 1, so
  // no optimal mark can exceed it. The big-M below comes from this bound.
  double L = std::pow(2.0, m) - 1;
  double M = L + 1;

  // the marks: the first mark is 0, the others lie in 0..L
  std::vector<dcp::Lin> a;
  a.push_back(dcp::new_var(h, 0, 0));
  for (int k = 1; k < m; ++k) a.push_back(dcp::new_var(h, 0, L));

  // marks strictly increase from left to right
  for (int k = 1; k < m; ++k) {
    // the next mark is at least one more than the previous mark
    dcp::add_row(h, a[k] - a[k - 1], 1, kHighsInf);
  }

  // every pair of differences a_j - a_i is distinct from every other pair
  // (a difference pair sharing its left or right mark is already distinct)
  std::vector<std::pair<int, int>> pairs;
  for (int i = 0; i < m; ++i)
    for (int j = i + 1; j < m; ++j) pairs.push_back({i, j});

  for (size_t p = 0; p < pairs.size(); ++p) {
    for (size_t q = p + 1; q < pairs.size(); ++q) {
      int i = pairs[p].first, j = pairs[p].second;
      int k = pairs[q].first, l = pairs[q].second;
      if (i == k || j == l) continue;

      // the difference a_j - a_i is different from the difference a_l - a_k:
      // binary b = 1 means the first is smaller, b = 0 means the second is smaller
      dcp::Lin d1 = a[j] - a[i];
      dcp::Lin d2 = a[l] - a[k];
      dcp::Lin b = dcp::new_var(h, 0, 1);
      dcp::add_row(h, d1 - d2 + M * b, -kHighsInf, M - 1);
      dcp::add_row(h, d2 - d1 - M * b, -kHighsInf, -1);
    }
  }

  // outputs: the marks and the length of the ruler (the last mark)
  out.add("marks", a);
  out.add("length", a[m - 1]);
  out.minimize(a[m - 1]);
}
