#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Fifty puzzle: each dummy carries a number. Choose which dummies to knock
// over so that the numbers on the knocked-over dummies add up to exactly the
// target sum.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int64_t target_sum = instance.at("target_sum").get<int64_t>();
  const std::vector<int64_t> values = instance.at("values").get<std::vector<int64_t>>();
  const int n = static_cast<int>(values.size());

  // dummies[i] is true when dummy i is knocked over.
  std::vector<BoolVar> dummies;
  for (int i = 0; i < n; ++i) dummies.push_back(model.NewBoolVar());

  // The numbers on the knocked-over dummies add up to the target sum.
  LinearExpr knocked_sum;
  for (int i = 0; i < n; ++i) knocked_sum += values[i] * dummies[i];
  model.AddEquality(knocked_sum, target_sum);

  json out = json::array();
  for (const BoolVar& d : dummies) out.push_back(d.index());
  outputs = {{"dummies", out}};
}
