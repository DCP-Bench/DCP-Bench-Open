#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Coin change: carry as few coins as possible while still being able to pay
// every amount from 1 up to max_amount_to_pay - 1 exactly.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<int64_t> denominations =
      instance.at("denominations").get<std::vector<int64_t>>();
  const int64_t max_amount_to_pay =
      instance.at("max_amount_to_pay").get<int64_t>();
  const int n = static_cast<int>(denominations.size());

  std::vector<IntVar> x;
  for (int i = 0; i < n; ++i) {
    x.push_back(model.NewIntVar(Domain(0, max_amount_to_pay)));
  }
  IntVar num_coins = model.NewIntVar(Domain(0, max_amount_to_pay));

  LinearExpr carried;
  for (int i = 0; i < n; ++i) carried += x[i];
  model.AddEquality(num_coins, carried);

  // One witness selection per payable amount, drawn from the coins carried.
  for (int64_t j = 1; j < max_amount_to_pay; ++j) {
    LinearExpr paid;
    for (int i = 0; i < n; ++i) {
      IntVar use = model.NewIntVar(Domain(0, max_amount_to_pay));
      model.AddLessOrEqual(use, x[i]);
      paid += denominations[i] * use;
    }
    model.AddEquality(paid, j);
  }

  model.Minimize(num_coins);

  json out = json::array();
  for (const IntVar& xi : x) out.push_back(xi.index());
  outputs = {{"x", out}};
}
