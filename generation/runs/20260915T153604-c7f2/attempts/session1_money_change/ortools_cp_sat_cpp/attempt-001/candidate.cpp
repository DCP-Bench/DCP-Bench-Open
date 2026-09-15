#include <algorithm>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Money change: make the amount exactly from the coins on hand, using as few
// coins as possible.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int64_t amount = instance.at("amount").get<int64_t>();
  const std::vector<int64_t> types_of_coins =
      instance.at("types_of_coins").get<std::vector<int64_t>>();
  const std::vector<int64_t> available_coins =
      instance.at("available_coins").get<std::vector<int64_t>>();
  const int n = static_cast<int>(types_of_coins.size());

  const int64_t max_available =
      *std::max_element(available_coins.begin(), available_coins.end());
  std::vector<IntVar> coin_counts;
  for (int i = 0; i < n; ++i) {
    coin_counts.push_back(model.NewIntVar(Domain(0, max_available)));
  }

  LinearExpr paid;
  LinearExpr handed_over;
  int64_t coin_bound = 0;
  for (int i = 0; i < n; ++i) {
    paid += types_of_coins[i] * coin_counts[i];
    handed_over += coin_counts[i];
    coin_bound += available_coins[i];
    model.AddLessOrEqual(coin_counts[i], available_coins[i]);
  }
  model.AddEquality(paid, amount);

  IntVar total_coins = model.NewIntVar(Domain(0, coin_bound));
  model.AddEquality(total_coins, handed_over);
  model.Minimize(total_coins);

  json out = json::array();
  for (const IntVar& c : coin_counts) out.push_back(c.index());
  outputs = {{"coin_counts", out}};
}
