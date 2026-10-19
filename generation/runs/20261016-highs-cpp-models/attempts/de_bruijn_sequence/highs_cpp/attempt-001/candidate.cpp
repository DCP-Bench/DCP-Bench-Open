// Problem: de Bruijn sequence. Print the de Bruijn sequence B(k, n) of order n on an
// alphabet of size k as a list of integers: a cyclic sequence of length k^n in which
// every possible length-n string on the alphabet occurs exactly once as a substring.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  // base = alphabet size k, n = order; both come from the instance.
  int k = instance.at("base").get<int>();
  int n = instance.at("n").get<int>();

  // L = k^n is the sequence length and also the number of length-n words.
  int L = 1;
  for (int i = 0; i < n; i++) L *= k;

  // A word read from a window has value sum_j digit_j * k^(n-1-j); pw[j] is that weight.
  std::vector<int> pw(n);
  pw[n - 1] = 1;
  for (int j = n - 2; j >= 0; j--) pw[j] = pw[j + 1] * k;

  // x[p][v] = 1 when position p of the cyclic sequence holds digit v.
  std::vector<std::vector<dcp::Lin>> x(L, std::vector<dcp::Lin>(k));
  for (int p = 0; p < L; p++)
    for (int v = 0; v < k; v++) x[p][v] = dcp::new_var(h, 0, 1);

  // each position holds exactly one digit
  for (int p = 0; p < L; p++) {
    dcp::Lin one;
    for (int v = 0; v < k; v++) one = one + x[p][v];
    dcp::add_row(h, one, 1, 1);
  }

  // z[p][w] = 1 when the length-n window starting at position p (cyclically) reads word w
  std::vector<std::vector<dcp::Lin>> z(L, std::vector<dcp::Lin>(L));
  for (int p = 0; p < L; p++)
    for (int w = 0; w < L; w++) z[p][w] = dcp::new_var(h, 0, 1);

  // each window reads exactly one word
  for (int p = 0; p < L; p++) {
    dcp::Lin one;
    for (int w = 0; w < L; w++) one = one + z[p][w];
    dcp::add_row(h, one, 1, 1);
  }

  // every word is read by at most one window; there are L windows and L words,
  // so every word is read by exactly one window
  for (int w = 0; w < L; w++) {
    dcp::Lin at_most_one;
    for (int p = 0; p < L; p++) at_most_one = at_most_one + z[p][w];
    dcp::add_row(h, at_most_one, -kHighsInf, 1);
  }

  // a window can read word w only if its digits are the digits of w:
  // the digit at window offset j is digit d = (w / k^(n-1-j)) mod k
  for (int p = 0; p < L; p++)
    for (int w = 0; w < L; w++)
      for (int j = 0; j < n; j++) {
        int q = (p + j) % L;
        int d = (w / pw[j]) % k;
        dcp::add_row(h, z[p][w] - x[q][d], -kHighsInf, 0);
      }

  // output: the digit at each position of the sequence
  std::vector<dcp::Lin> seq(L);
  for (int p = 0; p < L; p++) {
    dcp::Lin digit;
    for (int v = 0; v < k; v++) digit = digit + double(v) * x[p][v];
    seq[p] = digit;
  }
  out.add("de_bruijn", seq);
}
