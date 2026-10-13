// CMO 2012: find positive integers a, b, n, p with a - b = p prime, a * b = n^2 and a at least min_a, minimizing a.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int min_a = instance.at("min_a");
  int max_val = instance.at("max_val");

  // every value a, b, n and p is at most max_val (the instance bound); a is at least min_a and b at least 1
  IntVar* a = newIntVar(min_a, max_val);
  IntVar* b = newIntVar(1, max_val);
  IntVar* n = newIntVar(1, max_val);
  IntVar* p = newIntVar(2, max_val);

  // p is the difference a - b
  vec<int> diff_coef;
  diff_coef.push(1);
  diff_coef.push(-1);
  vec<IntVar*> ab_pair;
  ab_pair.push(a);
  ab_pair.push(b);
  int_linear(diff_coef, ab_pair, IRT_EQ, p);

  // p must be a prime number: the primes up to max_val are listed by a sieve on the instance bound
  std::vector<bool> composite(max_val + 1, false);
  for (int i = 2; i * i <= max_val; ++i) {
    if (!composite[i]) {
      for (int j = i * i; j <= max_val; j += i) composite[j] = true;
    }
  }
  vec<vec<int>> prime_rows;
  for (int q = 2; q <= max_val; ++q) {
    if (!composite[q]) {
      prime_rows.push();
      prime_rows.last().push(q);
    }
  }
  vec<IntVar*> p_only;
  p_only.push(p);
  table(p_only, prime_rows);

  // the product a * b is a perfect square n^2
  IntVar* ab = newIntVar(0, max_val * max_val);
  int_times(a, b, ab);
  IntVar* nn = newIntVar(0, max_val * max_val);
  int_times(n, n, nn);
  int_rel(ab, IRT_EQ, nn);

  // search on a and b; the rest follows from them
  vec<IntVar*> decision;
  decision.push(a);
  decision.push(b);
  branch(decision, VAR_INORDER, VAL_MIN);

  // a is the smallest value that admits a solution
  optimize(a, OPT_MIN);

  outputs = {{"a", dcp::out(a)}, {"b", dcp::out(b)}, {"n", dcp::out(n)}, {"p", dcp::out(p)}};
}
