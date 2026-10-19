#include "dcp.h"

// Find the smallest a with min_a <= a <= max_val, and integers b, n, p with
// b >= 1, a - b = p prime, and a * b = n * n.
//
// Why the search is over t: write g = gcd(a, b), a = g s^2 and b = g t^2 with
// gcd(s, t) = 1, because a * b is a square and the two parts are coprime. Then
// a - b = g (s^2 - t^2) is prime, so g divides p and g is 1 or p. g = p gives
// s^2 - t^2 = 1, which needs t = 0 and is excluded by b >= 1. So g = 1, and
// (s - t)(s + t) = p forces s = t + 1 and p = 2t + 1. The solutions are therefore
// a = (t + 1)^2, b = t^2, n = t (t + 1), p = 2t + 1, for t >= 1 with 2t + 1 prime.
// Each such t is one binary choice, so the model picks exactly one t.

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int min_a = instance.at("min_a").get<int>();
  int max_val = instance.at("max_val").get<int>();

  // primes up to max_val + 1 (2t + 1 is at most max_val + 1 when a <= max_val)
  int sieve_top = max_val + 1;
  std::vector<bool> composite(sieve_top + 1, false);
  for (int i = 2; i <= sieve_top; i++) {
    if (composite[i]) continue;
    for (long long j = static_cast<long long>(i) * i; j <= sieve_top; j += i) composite[j] = true;
  }

  // one binary per candidate t: t >= 1, a = (t + 1)^2 within min_a..max_val, 2t + 1 prime
  dcp::Lin a, b, n, p, chosen;
  for (int t = 1; (t + 1) * (t + 1) <= max_val; t++) {
    int prime_q = 2 * t + 1;
    if (composite[prime_q]) continue;
    long long a_t = static_cast<long long>(t + 1) * (t + 1);
    if (a_t < min_a) continue;
    dcp::Lin u = dcp::new_var(h, 0, 1);
    chosen = chosen + u;
    a = a + static_cast<double>(a_t) * u;
    b = b + static_cast<double>(t) * t * u;
    n = n + static_cast<double>(t) * (t + 1) * u;
    p = p + static_cast<double>(prime_q) * u;
  }

  // exactly one candidate is chosen
  dcp::add_row(h, chosen, 1, 1);

  out.add("a", a);
  out.add("b", b);
  out.add("n", n);
  out.add("p", p);
  out.minimize(a);
}
