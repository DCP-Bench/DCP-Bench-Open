#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Knapsack: pick items to maximize total value without exceeding the pack's
// weight capacity.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<int64_t> values =
      instance.at("values").get<std::vector<int64_t>>();
  const std::vector<int64_t> weights =
      instance.at("weights").get<std::vector<int64_t>>();
  const int64_t capacity = instance.at("capacity").get<int64_t>();
  const int n = static_cast<int>(values.size());

  std::vector<BoolVar> take;
  take.reserve(n);
  for (int i = 0; i < n; ++i) take.push_back(model.NewBoolVar());

  LinearExpr total_weight;
  LinearExpr total_value;
  for (int i = 0; i < n; ++i) {
    total_weight += weights[i] * take[i];
    total_value += values[i] * take[i];
  }
  model.AddLessOrEqual(total_weight, capacity);
  model.Maximize(total_value);

  json x_out = json::array();
  for (const BoolVar& b : take) x_out.push_back(b.index());
  outputs = {{"x", x_out}};
}
