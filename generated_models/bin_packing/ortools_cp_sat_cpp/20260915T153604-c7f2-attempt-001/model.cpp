#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Bin packing: assign each item to a bin without overloading any bin.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<int64_t> weights =
      instance.at("weights").get<std::vector<int64_t>>();
  const int64_t capacity = instance.at("capacity").get<int64_t>();
  const int num_bins = instance.at("num_bins").get<int>();
  const int n = static_cast<int>(weights.size());

  std::vector<IntVar> bins;
  bins.reserve(n);
  for (int j = 0; j < n; ++j) {
    bins.push_back(model.NewIntVar(Domain(0, num_bins - 1)));
  }

  // The reference ranges the capacity constraint over the item count rather
  // than the bin count; indices beyond num_bins - 1 are then vacuous.  Mirror
  // that range so the two models constrain exactly the same bins.
  for (int i = 0; i < n; ++i) {
    LinearExpr load;
    for (int j = 0; j < n; ++j) {
      BoolVar here = model.NewBoolVar();
      model.AddEquality(bins[j], i).OnlyEnforceIf(here);
      model.AddNotEqual(bins[j], i).OnlyEnforceIf(here.Not());
      load += weights[j] * here;
    }
    model.AddLessOrEqual(load, capacity);
  }

  json bins_out = json::array();
  for (const IntVar& b : bins) bins_out.push_back(b.index());
  outputs = {{"bins", bins_out}};
}
