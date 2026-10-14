#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// CMO 2012: find positive integers a and b where a - b is a prime p and a * b
// is a perfect square n^2, with a as small as possible but at least min_a.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int64_t min_a = instance.at("min_a").get<int64_t>();
  const int64_t max_val = instance.at("max_val").get<int64_t>();

  // The primes below max_val, by a sieve of Eratosthenes.  p has to be one of
  // them, which is how the reference's prime list is used.
  std::vector<bool> composite(max_val + 1, false);
  std::vector<int64_t> prime_list;
  for (int64_t i = 2; i < max_val; ++i) {
    if (composite[i]) continue;
    prime_list.push_back(i);
    for (int64_t j = i * i; j < max_val; j += i) composite[j] = true;
  }

  // Domains follow the reference: a from min_a, b positive, n from 0, and p
  // restricted to the prime list (2..max_val).
  IntVar a = model.NewIntVar(Domain(min_a, max_val));
  IntVar b = model.NewIntVar(Domain(1, max_val));
  IntVar n = model.NewIntVar(Domain(0, max_val));
  IntVar p = model.NewIntVar(Domain::FromValues(prime_list));

  // a is at least b.
  model.AddGreaterOrEqual(a, b);
  // a - b is the prime p.
  model.AddEquality(p, a - b);
  // The product a * b equals n * n (a perfect square).
  IntVar product = model.NewIntVar(Domain(0, max_val * max_val));
  model.AddMultiplicationEquality(product, a, b);
  model.AddMultiplicationEquality(product, n, n);

  // Find the smallest a.
  model.Minimize(a);

  outputs = {{"a", a.index()}, {"b", b.index()}, {"n", n.index()}, {"p", p.index()}};
}
