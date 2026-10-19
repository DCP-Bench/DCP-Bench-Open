// Binary sequence of length n with periodic autocorrelations C_k; minimise E = sum_{k=1}^{n-1} C_k^2.
// Each bit is +1 or -1. A binary b_i encodes it: the bit is S_i = 2 b_i - 1.
#include "dcp.h"

using dcp::Lin;

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n").get<int>();
  const double inf = kHighsInf;

  // the bits: b_i = 1 means S_i = +1, so S_i = 2 b_i - 1
  std::vector<Lin> b(n);
  for (int i = 0; i < n; ++i) b[i] = dcp::new_var(h, 0, 1);
  std::vector<Lin> S(n);
  for (int i = 0; i < n; ++i) S[i] = 2 * b[i] - 1;

  // d_ij is 1 when bits i and j differ (exclusive or), so S_i S_j = 1 - 2 d_ij
  std::vector<std::vector<Lin>> d(n, std::vector<Lin>(n));
  for (int i = 0; i < n; ++i) {
    for (int j = i + 1; j < n; ++j) {
      d[i][j] = dcp::new_var(h, 0, 1);
      d[j][i] = d[i][j];
      // d_ij >= b_i - b_j
      dcp::add_row(h, d[i][j] - b[i] + b[j], 0, inf);
      // d_ij >= b_j - b_i
      dcp::add_row(h, d[i][j] - b[j] + b[i], 0, inf);
      // d_ij <= b_i + b_j
      dcp::add_row(h, d[i][j] - b[i] - b[j], -inf, 0);
      // d_ij <= 2 - b_i - b_j
      dcp::add_row(h, d[i][j] + b[i] + b[j], -inf, 2);
    }
  }

  // For k = 1..n-1: C_k = sum_i S_i S_{(i+k) mod n} = n - 2 D_k, where D_k is the number of
  // i with bits i and (i+k) mod n differing. C_k is an integer of the parity of n, so the
  // tangent cuts Q_k >= 2 v C_k - v^2 at every v of that parity in [-n, n] give Q_k >= C_k^2
  // exactly, and Q_k stands for C_k squared.
  std::vector<Lin> C(n), Q(n);
  Lin energy;
  for (int k = 1; k < n; ++k) {
    Lin D;
    for (int i = 0; i < n; ++i) D = D + d[i][(i + k) % n];
    // C_k = n - 2 D_k
    C[k] = dcp::new_var(h, -n, n);
    dcp::add_row(h, C[k] + 2.0 * D, n, n);
    // Q_k >= C_k^2 by tangent cuts
    Q[k] = dcp::new_var(h, 0, double(n) * n, false);
    for (int v = -n; v <= n; v += 2) {
      dcp::add_row(h, Q[k] - 2.0 * v * C[k], -double(v) * v, inf);
    }
    // E includes C_k squared
    energy = energy + Q[k];
  }

  // minimise E = sum over k = 1..n-1 of C_k squared
  out.minimize(energy);
  // the sequence S_0 .. S_{n-1}, each +1 or -1
  out.add("sequence", S);
}
