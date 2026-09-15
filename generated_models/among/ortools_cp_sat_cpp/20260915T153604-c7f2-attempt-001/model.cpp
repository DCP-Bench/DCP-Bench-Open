#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Among: exactly m of the n entries of x must take a value drawn from v; the
// rest are free within the domain.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();
  const int64_t m = instance.at("m").get<int64_t>();
  const std::vector<int64_t> v = instance.at("v").get<std::vector<int64_t>>();

  // Domain 0..7 comes from the problem statement, which fixes it for every
  // instance; the reference declares the same range.
  std::vector<IntVar> x;
  x.reserve(n);
  for (int i = 0; i < n; ++i) x.push_back(model.NewIntVar(Domain(0, 7)));

  // Count the (position, wanted value) hits exactly as the reference does.
  LinearExpr hits;
  for (int i = 0; i < n; ++i) {
    for (const int64_t value : v) {
      BoolVar hit = model.NewBoolVar();
      model.AddEquality(x[i], value).OnlyEnforceIf(hit);
      model.AddNotEqual(x[i], value).OnlyEnforceIf(hit.Not());
      hits += hit;
    }
  }
  model.AddEquality(hits, m);

  json x_out = json::array();
  for (const IntVar& xi : x) x_out.push_back(xi.index());
  outputs = {{"x", x_out}};
}
