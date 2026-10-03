#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Even Fibonacci numbers (Project Euler 2): the sum of the even-valued
// Fibonacci terms that do not exceed four million.
// The problem has no instance data. As in the statement's model, the sequence
// is taken to 35 terms (f[35] = 9227465 is past the limit) with values bounded
// by 10^7, and starts f[0] = 0, f[1] = f[2] = 1.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const int n = 35;
  const int limit = 4000000;

  std::vector<IntVar> f;   // the Fibonacci terms
  std::vector<BoolVar> x;  // x[i]: term i is even and below four million
  for (int i = 0; i <= n; ++i) {
    f.push_back(model.NewIntVar(Domain(0, 10000000)));
    x.push_back(model.NewBoolVar());
  }
  const IntVar res = model.NewIntVar(Domain(0, 100000000));

  // The sequence starts 0, 1, 1 and term 0 is not counted.
  model.AddEquality(f[0], 0);
  model.AddEquality(f[1], 1);
  model.AddEquality(f[2], 1);
  model.AddEquality(x[0], 0);

  // Each new term is the sum of the previous two.
  for (int i = 3; i <= n; ++i) model.AddEquality(f[i], f[i - 1] + f[i - 2]);

  // x[i] holds exactly when term i is even and below four million. Evenness is
  // f[i] == 2 * half[i] for an integer half[i]; both directions are reified.
  for (int i = 1; i <= n; ++i) {
    const IntVar half = model.NewIntVar(Domain(0, 5000000));
    const IntVar remainder = model.NewIntVar(Domain(0, 1));
    model.AddEquality(f[i], 2 * half + remainder);
    const BoolVar even = model.NewBoolVar();
    model.AddEquality(remainder, 0).OnlyEnforceIf(even);
    model.AddEquality(remainder, 1).OnlyEnforceIf(even.Not());
    const BoolVar small = model.NewBoolVar();
    model.AddLessThan(f[i], limit).OnlyEnforceIf(small);
    model.AddGreaterOrEqual(f[i], limit).OnlyEnforceIf(small.Not());
    // x[i] == even & small
    model.AddBoolAnd({even, small}).OnlyEnforceIf(x[i]);
    model.AddBoolOr({even.Not(), small.Not()}).OnlyEnforceIf(x[i].Not());
  }

  // The answer is the sum of the counted terms.
  LinearExpr sum;
  for (int i = 1; i <= n; ++i) {
    const IntVar counted = model.NewIntVar(Domain(0, 10000000));
    model.AddEquality(counted, f[i]).OnlyEnforceIf(x[i]);
    model.AddEquality(counted, 0).OnlyEnforceIf(x[i].Not());
    sum += counted;
  }
  model.AddEquality(res, sum);

  outputs = {{"res", res.index()}};
}
