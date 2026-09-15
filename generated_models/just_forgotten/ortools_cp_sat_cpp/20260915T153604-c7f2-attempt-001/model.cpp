#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Just forgotten: recover a permutation of the digits, given several guesses
// that each got the same number of positions right.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<std::vector<int64_t>> sets =
      instance.at("sets").get<std::vector<std::vector<int64_t>>>();
  const int64_t num_correct_digits =
      instance.at("num_correct_digits").get<int64_t>();
  const int n = sets.empty() ? 0 : static_cast<int>(sets[0].size());

  std::vector<IntVar> x;
  for (int i = 0; i < n; ++i) x.push_back(model.NewIntVar(Domain(0, n - 1)));
  model.AddAllDifferent(x);

  for (const std::vector<int64_t>& guess : sets) {
    LinearExpr correct;
    for (int i = 0; i < n; ++i) {
      BoolVar hit = model.NewBoolVar();
      model.AddEquality(x[i], guess[i]).OnlyEnforceIf(hit);
      model.AddNotEqual(x[i], guess[i]).OnlyEnforceIf(hit.Not());
      correct += hit;
    }
    model.AddEquality(correct, num_correct_digits);
  }

  json out = json::array();
  for (const IntVar& xi : x) out.push_back(xi.index());
  outputs = {{"x", out}};
}
