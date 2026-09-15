#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Steiner triple system: n(n-1)/6 triples drawn from n items, no two triples
// sharing more than one item.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();
  const int n_sets = n * (n - 1) / 6;

  std::vector<std::vector<BoolVar>> sets(n_sets);
  for (int i = 0; i < n_sets; ++i) {
    for (int j = 0; j < n; ++j) sets[i].push_back(model.NewBoolVar());
  }

  for (int i = 0; i < n_sets; ++i) {
    LinearExpr size;
    for (int j = 0; j < n; ++j) size += sets[i][j];
    model.AddEquality(size, 3);
  }

  // Two triples overlap in at most one item; the overlap indicator per item is
  // the conjunction of the two membership variables.
  for (int i = 0; i < n_sets; ++i) {
    for (int k = i + 1; k < n_sets; ++k) {
      LinearExpr overlap;
      for (int j = 0; j < n; ++j) {
        BoolVar both = model.NewBoolVar();
        model.AddBoolAnd({sets[i][j], sets[k][j]}).OnlyEnforceIf(both);
        model.AddBoolOr({sets[i][j].Not(), sets[k][j].Not()})
            .OnlyEnforceIf(both.Not());
        overlap += both;
      }
      model.AddLessOrEqual(overlap, 1);
    }
  }

  json out = json::array();
  for (int i = 0; i < n_sets; ++i) {
    json row = json::array();
    for (int j = 0; j < n; ++j) row.push_back(sets[i][j].index());
    out.push_back(row);
  }
  outputs = {{"sets", out}};
}
