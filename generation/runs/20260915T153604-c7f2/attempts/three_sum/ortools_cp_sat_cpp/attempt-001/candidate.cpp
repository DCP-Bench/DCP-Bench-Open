#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Three sum: pick exactly m of the numbers so that they add up to zero.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<int64_t> nums =
      instance.at("nums").get<std::vector<int64_t>>();
  const int64_t m = instance.at("m").get<int64_t>();
  const int n = static_cast<int>(nums.size());

  std::vector<BoolVar> indices;
  for (int i = 0; i < n; ++i) indices.push_back(model.NewBoolVar());

  LinearExpr total;
  LinearExpr picked;
  for (int i = 0; i < n; ++i) {
    total += nums[i] * indices[i];
    picked += indices[i];
  }
  model.AddEquality(total, 0);
  model.AddEquality(picked, m);

  json out = json::array();
  for (const BoolVar& b : indices) out.push_back(b.index());
  outputs = {{"indices", out}};
}
