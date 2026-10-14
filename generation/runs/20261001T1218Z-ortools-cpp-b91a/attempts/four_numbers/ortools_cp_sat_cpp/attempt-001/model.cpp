#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Four numbers: given up to four distinct integers between 1 and 10, find
// three integers between 1 and 10 such that every given number is the sum of
// some subset of the three.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<int64_t> numbers = instance.at("numbers").get<std::vector<int64_t>>();
  const int m = static_cast<int>(numbers.size());
  const int n = 3;  // the number of integers to find, fixed by the problem statement

  // x[j] is the j-th of the three integers, between 1 and 10 (problem constants).
  std::vector<IntVar> x;
  for (int j = 0; j < n; ++j) x.push_back(model.NewIntVar(Domain(1, 10)));

  // tmp[i][j] is true when x[j] is one of the integers summed to make numbers[i].
  std::vector<std::vector<BoolVar>> tmp(m);
  for (int i = 0; i < m; ++i)
    for (int j = 0; j < n; ++j) tmp[i].push_back(model.NewBoolVar());

  // Each given number is the sum of the chosen subset of x. The term
  // tmp * x is a Boolean times a variable, so it gets its own variable:
  // equal to x[j] when tmp is true and to 0 when tmp is false.
  for (int i = 0; i < m; ++i) {
    LinearExpr subset_sum;
    for (int j = 0; j < n; ++j) {
      const IntVar term = model.NewIntVar(Domain(0, 10));
      model.AddEquality(term, x[j]).OnlyEnforceIf(tmp[i][j]);
      model.AddEquality(term, 0).OnlyEnforceIf(tmp[i][j].Not());
      subset_sum += term;
    }
    model.AddEquality(subset_sum, numbers[i]);
  }

  json out = json::array();
  for (const IntVar& v : x) out.push_back(v.index());
  outputs = {{"x", out}};
}
