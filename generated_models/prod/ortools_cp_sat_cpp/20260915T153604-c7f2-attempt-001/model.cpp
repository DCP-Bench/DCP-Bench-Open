#include <algorithm>
#include <numeric>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Production planning: choose quantities within per-product ceilings so that
// the shared production rate constraint holds, maximizing profit.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<int64_t> a = instance.at("a").get<std::vector<int64_t>>();
  const std::vector<int64_t> c = instance.at("c").get<std::vector<int64_t>>();
  const std::vector<int64_t> u = instance.at("u").get<std::vector<int64_t>>();
  const int64_t b = instance.at("b").get<int64_t>();
  const int num_products = static_cast<int>(a.size());

  const int64_t max_u = *std::max_element(u.begin(), u.end());
  std::vector<IntVar> x;
  for (int j = 0; j < num_products; ++j) {
    x.push_back(model.NewIntVar(Domain(0, max_u)));
  }

  // The rate constraint is sum(x[j] / a[j]) <= b.  Multiplying through by the
  // least common multiple of a clears the divisions without rounding.
  int64_t lcm_a = 1;
  for (const int64_t aj : a) lcm_a = std::lcm(lcm_a, aj);
  LinearExpr rate;
  for (int j = 0; j < num_products; ++j) rate += (lcm_a / a[j]) * x[j];
  model.AddLessOrEqual(rate, b * lcm_a);

  for (int j = 0; j < num_products; ++j) {
    model.AddGreaterOrEqual(x[j], 0);
    model.AddLessOrEqual(x[j], u[j]);
  }

  int64_t profit_bound = 0;
  LinearExpr profit;
  for (int j = 0; j < num_products; ++j) {
    profit += c[j] * x[j];
    profit_bound += c[j] * max_u;
  }
  IntVar total_profit = model.NewIntVar(Domain(0, profit_bound));
  model.AddEquality(total_profit, profit);
  model.Maximize(total_profit);

  json x_out = json::array();
  for (const IntVar& xj : x) x_out.push_back(xj.index());
  outputs = {{"x", x_out}, {"total_profit", total_profit.index()}};
}
