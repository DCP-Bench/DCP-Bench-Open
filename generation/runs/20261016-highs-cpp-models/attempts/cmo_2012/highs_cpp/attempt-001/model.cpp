#include "dcp.h"

// Find the smallest a with min_a <= a <= max_val, and integers b, n, p with
// 1 <= b, a - b = p prime, and a * b = n * n.
// a, b and n are at most max_val (the instance bound on the values).

// Returns z = x * bit, for an integer x in [0, M] and a binary bit (exact).
static dcp::Lin times_bit(Highs& h, const dcp::Lin& x, const dcp::Lin& bit, double M) {
  dcp::Lin z = dcp::new_var(h, 0, M);
  // z is zero when bit is zero
  dcp::add_row(h, z - M * bit, -kHighsInf, 0);
  // z is at most x
  dcp::add_row(h, z - x, -kHighsInf, 0);
  // when bit is one, z is at least x
  dcp::add_row(h, z - x - M * bit, -M, kHighsInf);
  return z;
}

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int min_a = instance.at("min_a").get<int>();
  int max_val = instance.at("max_val").get<int>();
  double M = max_val;

  // number of bits that hold every value up to max_val
  int K = 0;
  while ((1LL << K) <= max_val) K++;

  // a is between min_a and max_val
  dcp::Lin a = dcp::new_var(h, min_a, M);

  // b is written in binary bits, b = sum 2^k bb_k, and b is between 1 and max_val
  std::vector<dcp::Lin> bb;
  dcp::Lin b;
  for (int k = 0; k < K; k++) {
    bb.push_back(dcp::new_var(h, 0, 1));
    b = b + static_cast<double>(1LL << k) * bb[k];
  }
  dcp::add_row(h, b, 1, M);

  // n is written in binary bits, n = sum 2^j mb_j, and n is between 0 and max_val
  std::vector<dcp::Lin> mb;
  dcp::Lin n;
  for (int j = 0; j < K; j++) {
    mb.push_back(dcp::new_var(h, 0, 1));
    n = n + static_cast<double>(1LL << j) * mb[j];
  }
  dcp::add_row(h, n, 0, M);

  // a times b is n times n: both sides are sums of products with a bit
  // a * b = sum 2^k (a * bb_k)
  dcp::Lin ab;
  for (int k = 0; k < K; k++) {
    ab = ab + static_cast<double>(1LL << k) * times_bit(h, a, bb[k], M);
  }
  // n * n = sum 2^j (n * mb_j)
  dcp::Lin nn;
  for (int j = 0; j < K; j++) {
    nn = nn + static_cast<double>(1LL << j) * times_bit(h, n, mb[j], M);
  }
  // a * b equals n * n
  dcp::add_row(h, ab - nn, 0, 0);

  // p is a prime: p = sum q ind_q over the primes q up to max_val, exactly one indicator is on
  std::vector<bool> composite(max_val + 1, false);
  std::vector<int> primes;
  for (int i = 2; i <= max_val; i++) {
    if (composite[i]) continue;
    primes.push_back(i);
    for (long long j = static_cast<long long>(i) * i; j <= max_val; j += i) composite[j] = true;
  }
  std::vector<dcp::Lin> ind;
  dcp::Lin p;
  dcp::Lin one_prime;
  for (int q : primes) {
    dcp::Lin v = dcp::new_var(h, 0, 1);
    ind.push_back(v);
    p = p + static_cast<double>(q) * v;
    one_prime = one_prime + v;
  }
  // exactly one prime is chosen
  dcp::add_row(h, one_prime, 1, 1);

  // a minus b is p
  dcp::add_row(h, a - b - p, 0, 0);

  out.add("a", a);
  out.add("b", b);
  out.add("n", n);
  out.add("p", p);
  out.minimize(a);
}
