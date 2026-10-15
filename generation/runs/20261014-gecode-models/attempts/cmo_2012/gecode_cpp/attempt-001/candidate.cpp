#include "dcp.h"

// Find positive integers a, b, n, p with a - b = p prime, a * b = n^2 and b > 0,
// where a is at least min_a and the values are bounded by max_val; minimise a.
class SquareProductPrimeDifference : public dcp::Space {
 protected:
  IntVar a;  // the smallest value of a we look for
  IntVar b;  // the second positive integer
  IntVar n;  // a * b = n^2
  IntVar p;  // a - b, a prime number

 public:
  explicit SquareProductPrimeDifference(const json& instance) {
    int min_a = instance.at("min_a").get<int>();
    int max_val = instance.at("max_val").get<int>();

    // sieve of Eratosthenes: the primes up to max_val (a - b <= a <= max_val)
    std::vector<bool> composite(max_val + 1, false);
    std::vector<int> primes;
    for (int i = 2; i <= max_val; ++i) {
      if (composite[i]) continue;
      primes.push_back(i);
      for (long long j = 1LL * i * i; j <= max_val; j += i) composite[j] = true;
    }
    IntArgs prime_args(static_cast<int>(primes.size()));
    for (int i = 0; i < static_cast<int>(primes.size()); ++i) prime_args[i] = primes[i];

    // a is at least the given minimum; a and b are positive and at most max_val
    a = IntVar(*this, min_a, max_val);
    b = IntVar(*this, 1, max_val);
    n = IntVar(*this, 1, max_val);

    // a - b is a prime number
    p = IntVar(*this, IntSet(prime_args));
    rel(*this, a == b + p);

    // a * b is a perfect square n^2
    IntVar ab = expr(*this, a * b);
    IntVar nn = expr(*this, n * n);
    rel(*this, ab == nn);

    // branch on the smallest a first, then the square root and b, then the prime difference
    branch(*this, a, INT_VAL_MIN());
    branch(*this, n, INT_VAL_MIN());
    branch(*this, b, INT_VAL_MIN());
    branch(*this, p, INT_VAL_MIN());

    minimize(a);
    output("a", a);
    output("b", b);
    output("n", n);
    output("p", p);
  }

  SquareProductPrimeDifference(SquareProductPrimeDifference& s) : dcp::Space(s) {
    a.update(*this, s.a);
    b.update(*this, s.b);
    n.update(*this, s.n);
    p.update(*this, s.p);
  }
  Gecode::Space* copy() override { return new SquareProductPrimeDifference(*this); }
};

DCP_MODEL(SquareProductPrimeDifference)
