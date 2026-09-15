#include <algorithm>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Revenue maximization: sell fare packages within each package's demand and
// each flight leg's seat count, for the most revenue.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<int64_t> available_seats =
      instance.at("available_seats").get<std::vector<int64_t>>();
  const std::vector<int64_t> demand =
      instance.at("demand").get<std::vector<int64_t>>();
  const std::vector<int64_t> revenue =
      instance.at("revenue").get<std::vector<int64_t>>();
  const std::vector<std::vector<int64_t>> delta =
      instance.at("delta").get<std::vector<std::vector<int64_t>>>();
  const int num_packages = static_cast<int>(demand.size());
  const int num_legs = static_cast<int>(available_seats.size());

  const int64_t max_demand = *std::max_element(demand.begin(), demand.end());
  std::vector<IntVar> packages_to_sell;
  for (int i = 0; i < num_packages; ++i) {
    packages_to_sell.push_back(model.NewIntVar(Domain(0, max_demand)));
  }

  for (int j = 0; j < num_legs; ++j) {
    LinearExpr seats_used;
    for (int i = 0; i < num_packages; ++i) {
      seats_used += delta[i][j] * packages_to_sell[i];
    }
    model.AddLessOrEqual(seats_used, available_seats[j]);
  }
  for (int i = 0; i < num_packages; ++i) {
    model.AddLessOrEqual(packages_to_sell[i], demand[i]);
  }

  int64_t revenue_bound = 0;
  LinearExpr earned;
  for (int i = 0; i < num_packages; ++i) {
    earned += revenue[i] * packages_to_sell[i];
    revenue_bound += revenue[i] * demand[i];
  }
  IntVar max_revenue = model.NewIntVar(Domain(0, revenue_bound));
  model.AddEquality(max_revenue, earned);
  model.Maximize(max_revenue);

  json sold = json::array();
  for (const IntVar& p : packages_to_sell) sold.push_back(p.index());
  outputs = {{"packages_to_sell", sold}, {"max_revenue", max_revenue.index()}};
}
