#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Magic sequence: a self-describing sequence where x[i] counts how many times
// the value i occurs in x.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();

  std::vector<IntVar> x;
  for (int i = 0; i < n; ++i) x.push_back(model.NewIntVar(Domain(0, n - 1)));

  // occurs[j][i] says whether position j holds the value i.
  std::vector<std::vector<BoolVar>> occurs(n);
  for (int j = 0; j < n; ++j) {
    for (int i = 0; i < n; ++i) {
      BoolVar hit = model.NewBoolVar();
      model.AddEquality(x[j], i).OnlyEnforceIf(hit);
      model.AddNotEqual(x[j], i).OnlyEnforceIf(hit.Not());
      occurs[j].push_back(hit);
    }
  }

  for (int i = 0; i < n; ++i) {
    LinearExpr count;
    for (int j = 0; j < n; ++j) count += occurs[j][i];
    model.AddEquality(x[i], count);
  }

  json out = json::array();
  for (const IntVar& xi : x) out.push_back(xi.index());
  outputs = {{"x", out}};
}
