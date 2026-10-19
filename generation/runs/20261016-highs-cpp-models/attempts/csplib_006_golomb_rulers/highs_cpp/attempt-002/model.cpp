// csplib_006_golomb_rulers: a Golomb ruler with m marks 0 = a_1 < ... < a_m whose
// pairwise differences are all distinct; minimise the length a_m.
#include "dcp.h"

#include <algorithm>
#include <cmath>

// Upper bound on the length: a known Sidon set (Erdos-Turan construction
// 2*p*i + (i*i mod p), i = 0..m-1, p the smallest prime >= m). Its length is a
// feasible ruler length, so the optimum is at most that length. The set is checked
// for distinct differences at run time; if the check fails the greedy bound 2^m - 1
// is used instead.
static double ruler_upper_bound(int m) {
  double greedy = std::pow(2.0, m) - 1;
  int p = std::max(m, 2);
  for (;; ++p) {
    bool prime = true;
    for (int d = 2; d * d <= p; ++d)
      if (p % d == 0) { prime = false; break; }
    if (prime) break;
  }
  std::vector<long> marks;
  for (int i = 0; i < m; ++i)
    marks.push_back(2L * p * i + (static_cast<long>(i) * i) % p);
  std::vector<long> diffs;
  for (int i = 0; i < m; ++i)
    for (int j = i + 1; j < m; ++j) diffs.push_back(marks[j] - marks[i]);
  std::sort(diffs.begin(), diffs.end());
  for (size_t k = 1; k < diffs.size(); ++k)
    if (diffs[k] == diffs[k - 1]) return greedy;
  return std::min(greedy, static_cast<double>(marks[m - 1]));
}

// Depth-first search for a ruler with m marks and length at most lim (node budget
// applies). Any ruler it finds is feasible, so its length bounds the optimum.
static bool ruler_dfs(int m, int k, int last, int lim, std::vector<int>& marks,
                      std::vector<char>& used, long& nodes) {
  if (k == m) return true;
  if (++nodes > 2000000) return false;
  for (int p = last + 1; p <= lim - (m - 1 - k); ++p) {
    std::vector<int> added;
    bool ok = true;
    for (int i = 0; i < k && ok; ++i) {
      int d = p - marks[i];
      if (used[d]) ok = false;
      else { used[d] = 1; added.push_back(d); }
    }
    if (ok) {
      marks.push_back(p);
      if (ruler_dfs(m, k + 1, p, lim, marks, used, nodes)) return true;
      marks.pop_back();
    }
    for (int d : added) used[d] = 0;
    if (nodes > 2000000) return false;
  }
  return false;
}

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int m = instance.at("size").get<int>();

  // L bounds every mark. A ruler of length L has all m(m-1)/2 differences in 1..L,
  // so L is also at least m(m-1)/2 in any optimal solution.
  int L0 = static_cast<int>(ruler_upper_bound(m));
  int L = L0;
  {
    std::vector<int> marks{0};
    std::vector<char> used(L0 + 1, 0);
    long nodes = 0;
    if (ruler_dfs(m, 1, 0, L0, marks, used, nodes)) L = marks.back();
  }
  double M = L;  // differences of two rulers in 0..L differ by at most L

  // the marks: the first mark is 0. Mark k (0-based) is at least k (strictly
  // increasing integers) and at most L minus the room the later marks need.
  std::vector<dcp::Lin> a;
  a.push_back(dcp::new_var(h, 0, 0));
  for (int k = 1; k < m; ++k)
    a.push_back(dcp::new_var(h, k, L - (m - 1 - k)));

  // marks strictly increase from left to right
  for (int k = 1; k < m; ++k) {
    // the next mark is at least one more than the previous mark
    dcp::add_row(h, a[k] - a[k - 1], 1, kHighsInf);
  }

  // the length is at least m(m-1)/2: that many distinct positive differences fit in it
  dcp::add_row(h, a[m - 1], m * (m - 1) / 2.0, kHighsInf);

  // reflection symmetry: reading the ruler backwards gives another ruler of the same
  // length, so the first gap may be taken no larger than the last gap
  if (m >= 3) dcp::add_row(h, a[1] - a[0] - (a[m - 1] - a[m - 2]), -kHighsInf, 0);

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
