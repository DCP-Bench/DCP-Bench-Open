#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Subset sum: how many bags of each coin type were stolen, given the total
// number of coins lost.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int64_t total_coins_lost =
      instance.at("total_coins_lost").get<int64_t>();
  const std::vector<int64_t> coin_numbers =
      instance.at("coin_numbers").get<std::vector<int64_t>>();
  const int n = static_cast<int>(coin_numbers.size());

  std::vector<IntVar> bags;
  for (int i = 0; i < n; ++i) {
    bags.push_back(model.NewIntVar(Domain(0, total_coins_lost)));
  }

  LinearExpr lost;
  for (int i = 0; i < n; ++i) lost += coin_numbers[i] * bags[i];
  model.AddEquality(lost, total_coins_lost);

  json out = json::array();
  for (const IntVar& b : bags) out.push_back(b.index());
  outputs = {{"bags", out}};
}
