#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Birthday coins: Tommy got 15 coins (half-crowns, shillings and sixpences)
// worth 1 pound 5 shillings 6 pence in total. How many half-crowns?
// The problem has no instance data: coin values and totals are part of the puzzle.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  // Coin values in pence: half-crown 30, shilling 12, sixpence 6.
  const std::vector<int64_t> values = {30, 12, 6};
  const int64_t total_value = 240 + 5 * 12 + 6;  // 1 pound 5 shillings 6 pence
  const int64_t total_coins = 15;

  // coins[k]: how many coins of kind k he received.
  std::vector<IntVar> coins;
  for (size_t k = 0; k < values.size(); ++k)
    coins.push_back(model.NewIntVar(Domain(0, total_coins)));

  // The coins add up to the total value.
  LinearExpr value;
  for (size_t k = 0; k < values.size(); ++k) value += values[k] * coins[k];
  model.AddEquality(value, total_value);

  // He received 15 coins.
  LinearExpr count;
  for (const IntVar& c : coins) count += c;
  model.AddEquality(count, total_coins);

  outputs = {{"half_crowns", coins[0].index()}};
}
