// csplib_084_hadamard_matrix: 2cc Hadamard matrix Legendre pairs for odd l, m = (l - 1) / 2.
// Find two sequences a = [a_1..a_l] and b = [b_1..b_l] with entries in {-1, +1} such that
// the periodic autocorrelations of a and b sum to -2 at every shift s = 1..m, the entries
// of a sum to 1, and the entries of b sum to 1. Satisfaction problem, no objective.
#include "dcp.h"

#include <vector>

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int l = instance.at("l").get<int>();
  int m = (l - 1) / 2;

  // Each entry is a binary x_i, and the sign value is a_i = 2 x_i - 1 (so -1 or +1).
  std::vector<dcp::Lin> xa, xb;
  for (int i = 0; i < l; i++) xa.push_back(dcp::new_var(h, 0, 1));
  for (int i = 0; i < l; i++) xb.push_back(dcp::new_var(h, 0, 1));

  // the entries of a sum to 1
  {
    dcp::Lin sum_a;
    for (int i = 0; i < l; i++) sum_a = sum_a + (2 * xa[i] - 1);
    dcp::add_row(h, sum_a, 1, 1);
  }
  // the entries of b sum to 1
  {
    dcp::Lin sum_b;
    for (int i = 0; i < l; i++) sum_b = sum_b + (2 * xb[i] - 1);
    dcp::add_row(h, sum_b, 1, 1);
  }

  // For each shift s = 1..m: the periodic autocorrelation of a at shift s plus that of b at shift s is -2.
  // A product of two signs a_i a_j = 4 x_i x_j - 2 x_i - 2 x_j + 1, where x_i x_j is a continuous
  // column p in [0, 1] pinned to the product of the binaries by three rows (exact for binaries).
  for (int s = 1; s <= m; s++) {
    dcp::Lin paf_sum;
    // autocorrelation of a at shift s, with index i + s taken mod l
    for (int i = 0; i < l; i++) {
      int j = (i + s) % l;
      dcp::Lin p = dcp::new_var(h, 0, 1, false);
      dcp::add_row(h, p - xa[i], -kHighsInf, 0);                     // p <= x_i
      dcp::add_row(h, p - xa[j], -kHighsInf, 0);                     // p <= x_j
      dcp::add_row(h, p - xa[i] - xa[j], -1, kHighsInf);             // p >= x_i + x_j - 1
      paf_sum = paf_sum + (4 * p - 2 * xa[i] - 2 * xa[j] + 1);
    }
    // autocorrelation of b at shift s, with index i + s taken mod l
    for (int i = 0; i < l; i++) {
      int j = (i + s) % l;
      dcp::Lin p = dcp::new_var(h, 0, 1, false);
      dcp::add_row(h, p - xb[i], -kHighsInf, 0);                     // p <= x_i
      dcp::add_row(h, p - xb[j], -kHighsInf, 0);                     // p <= x_j
      dcp::add_row(h, p - xb[i] - xb[j], -1, kHighsInf);             // p >= x_i + x_j - 1
      paf_sum = paf_sum + (4 * p - 2 * xb[i] - 2 * xb[j] + 1);
    }
    // PAF(a, s) + PAF(b, s) = -2
    dcp::add_row(h, paf_sum, -2, -2);
  }

  std::vector<dcp::Lin> a, b;
  for (int i = 0; i < l; i++) a.push_back(2 * xa[i] - 1);
  for (int i = 0; i < l; i++) b.push_back(2 * xb[i] - 1);
  out.add("a", a);
  out.add("b", b);
}
