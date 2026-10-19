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
static int ruler_upper_bound(int m) {
  int greedy = (1 << m) - 1;
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
  return std::min<long>(greedy, marks[m - 1]);
}

// Depth-first search for a ruler with m marks and length at most lim. It places
// marks left to right, keeps the differences distinct, and gives up after a fixed
// number of nodes. A ruler it finds is a feasible solution, so its length is a valid
// upper bound on the optimum.
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
  int L = ruler_upper_bound(m);
  {
    std::vector<int> marks{0};
    std::vector<char> used(L + 1, 0);
    long nodes = 0;
    if (ruler_dfs(m, 1, 0, L, marks, used, nodes)) L = marks.back();
  }

  // Position form. x[t] = 1 when the ruler has a mark at position t, for t in 0..L.
  // Mark 0 is at position 0.
  std::vector<dcp::Lin> x;
  for (int t = 0; t <= L; ++t) x.push_back(dcp::new_var(h, t == 0 ? 1 : 0, 1));

  // the ruler has exactly m marks
  dcp::Lin count = 0;
  for (int t = 0; t <= L; ++t) count = count + x[t];
  dcp::add_row(h, count, m, m);

  // window cut: the marks inside a window of width w have distinct differences in
  // 1..w, so n marks in the window give n(n-1)/2 <= w, i.e. n <= (1 + sqrt(1 + 8w)) / 2
  for (int w = 1; w <= L; ++w) {
    int nmax = static_cast<int>(std::floor((1 + std::sqrt(1.0 + 8.0 * w)) / 2 + 1e-9));
    if (nmax >= w + 1) continue;  // the window holds at most w + 1 positions anyway
    for (int s = 0; s + w <= L; ++s) {
      dcp::Lin win = 0;
      for (int t = s; t <= s + w; ++t) win = win + x[t];
      dcp::add_row(h, win, -kHighsInf, nmax);
    }
  }

  // every difference d is realised by at most one pair of marks. y[t][d] = 1 when
  // marks at t and t+d both exist, so y[t][d] >= x[t] + x[t+d] - 1. The sum of the
  // y over t for one d is at most one, so at most one pair has difference d.
  for (int d = 1; d <= L; ++d) {
    dcp::Lin pairs = 0;
    for (int t = 0; t + d <= L; ++t) {
      dcp::Lin y = dcp::new_var(h, 0, 1, false);
      // a mark at t and a mark at t + d give a pair with difference d
      dcp::add_row(h, x[t] + x[t + d] - y, -kHighsInf, 1);
      pairs = pairs + y;
    }
    // no two pairs of marks share the difference d
    dcp::add_row(h, pairs, -kHighsInf, 1);
  }

  // the marks in order: mark k (0-based) sits at a position a[k]. Each position t
  // with a mark is assigned to exactly one k, and each k to exactly one position.
  std::vector<std::vector<dcp::Lin>> e(L + 1, std::vector<dcp::Lin>(m));
  for (int t = 0; t <= L; ++t)
    for (int k = 0; k < m; ++k) e[t][k] = dcp::new_var(h, 0, 1);
  for (int t = 0; t <= L; ++t) {
    dcp::Lin s = 0;
    for (int k = 0; k < m; ++k) s = s + e[t][k];
    dcp::add_row(h, s - x[t], 0, 0);
  }
  std::vector<dcp::Lin> a;
  for (int k = 0; k < m; ++k) {
    dcp::Lin s = 0;
    dcp::Lin pos = 0;
    for (int t = 0; t <= L; ++t) {
      s = s + e[t][k];
      pos = pos + static_cast<double>(t) * e[t][k];
    }
    dcp::add_row(h, s, 1, 1);
    dcp::Lin ak = dcp::new_var(h, k, L - (m - 1 - k));
    dcp::add_row(h, ak - pos, 0, 0);
    a.push_back(ak);
  }

  // marks strictly increase: fixes the assignment of positions to k
  for (int k = 1; k < m; ++k) dcp::add_row(h, a[k] - a[k - 1], 1, kHighsInf);

  // the length is at least m(m-1)/2: that many distinct positive differences fit in it
  dcp::add_row(h, a[m - 1], m * (m - 1) / 2.0, kHighsInf);

  // reflection symmetry: reading the ruler backwards gives another ruler of the same
  // length, so the first gap may be taken no larger than the last gap
  if (m >= 3) dcp::add_row(h, a[1] - a[0] - (a[m - 1] - a[m - 2]), -kHighsInf, 0);

  // outputs: the marks and the length of the ruler (the last mark)
  out.add("marks", a);
  out.add("length", a[m - 1]);
  out.minimize(a[m - 1]);
}
