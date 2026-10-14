#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// N-fractions (CSPLib 41): find distinct non-zero digits A..I such that
// A/BC + D/EF + G/HI = 1, where BC, EF and HI are two-digit numbers.
// The problem has no instance data.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const int n = 9;
  std::vector<IntVar> x;
  for (int k = 0; k < n; ++k) x.push_back(model.NewIntVar(Domain(1, n)));
  const IntVar &A = x[0], &B = x[1], &C = x[2], &D = x[3], &E = x[4], &F = x[5], &G = x[6],
               &H = x[7], &I = x[8];

  // The denominators BC, EF and HI. Their domain is 1..81 (n * n), as the
  // problem's specification declares it, so denominators above 81 are excluded.
  const IntVar D1 = model.NewIntVar(Domain(1, n * n));
  const IntVar D2 = model.NewIntVar(Domain(1, n * n));
  const IntVar D3 = model.NewIntVar(Domain(1, n * n));

  // The digits are distinct.
  model.AddAllDifferent(x);

  // BC, EF and HI are the two-digit numbers formed by their digits.
  model.AddEquality(D1, 10 * B + C);
  model.AddEquality(D2, 10 * E + F);
  model.AddEquality(D3, 10 * H + I);

  // The fractions sum to 1, multiplied through by D1 * D2 * D3:
  // A * D2 * D3 + D * D1 * D3 + G * D1 * D2 == D1 * D2 * D3.
  // Every product is built two factors at a time.
  const int64_t pair_max = static_cast<int64_t>(n * n) * (n * n);
  auto product = [&](const IntVar& u, const IntVar& v, int64_t hi) {
    const IntVar r = model.NewIntVar(Domain(1, hi));
    model.AddMultiplicationEquality(r, {u, v});
    return r;
  };
  const IntVar d23 = product(D2, D3, pair_max);
  const IntVar d13 = product(D1, D3, pair_max);
  const IntVar d12 = product(D1, D2, pair_max);
  const IntVar term_a = product(A, d23, n * pair_max);
  const IntVar term_d = product(D, d13, n * pair_max);
  const IntVar term_g = product(G, d12, n * pair_max);
  const IntVar d123 = product(D1, d23, (n * n) * pair_max);
  model.AddEquality(term_a + term_d + term_g, d123);

  outputs = {{"A", A.index()}, {"B", B.index()}, {"C", C.index()},
             {"D", D.index()}, {"E", E.index()}, {"F", F.index()},
             {"G", G.index()}, {"H", H.index()}, {"I", I.index()}};
}
