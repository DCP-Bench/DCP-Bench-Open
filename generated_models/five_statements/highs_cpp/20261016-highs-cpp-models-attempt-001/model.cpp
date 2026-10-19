// Problem: five_statements. Determine which of the following statements is true.
//   Statement 1: exactly one of these statements is false.
//   Statement 2: exactly two of these statements are false.
//   Statement 3: exactly three of these statements are false.
//   Statement 4: exactly four of these statements are false.
//   Statement 5: exactly five of these statements are false.
// Output statements[i] is 1 when statement i+1 is true, 0 otherwise.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;  // the problem has a fixed size of five statements

  // s[i] = 1 when statement i+1 is true
  std::vector<dcp::Lin> s;
  for (int i = 0; i < 5; ++i) s.push_back(dcp::new_var(h, 0, 1));

  // T = number of true statements, so the number of false ones is 5 - T
  dcp::Lin T = dcp::new_var(h, 0, 5);
  // the number of true statements equals the sum of the statement values
  dcp::add_row(h, T - s[0] - s[1] - s[2] - s[3] - s[4], 0, 0);

  // statement k (k = 1..5) is true exactly when 5 - T = k, that is T = 5 - k
  // (the bounds of T are 0..5, so the gated equality below uses M = 5)
  for (int k = 1; k <= 5; ++k) {
    int t = 5 - k;
    dcp::Lin sk = s[k - 1];

    // if statement k is true then T = t
    // T >= t when s_k = 1
    dcp::add_row(h, T - 5 * sk, t - 5, kHighsInf);
    // T <= t when s_k = 1
    dcp::add_row(h, T + 5 * sk, -kHighsInf, t + 5);

    // if statement k is false then T != t
    // d_k = 1 means T >= t + 1, d_k = 0 means T <= t - 1 (relaxed when s_k = 1)
    dcp::Lin dk = dcp::new_var(h, 0, 1);
    // T <= t - 1 + 6 d_k + 6 s_k
    dcp::add_row(h, T - 6 * dk - 6 * sk, -kHighsInf, t - 1);
    // T >= (t + 1) d_k - 6 s_k
    dcp::add_row(h, T - (t + 1) * dk + 6 * sk, 0, kHighsInf);
  }

  out.add("statements", s);
}
