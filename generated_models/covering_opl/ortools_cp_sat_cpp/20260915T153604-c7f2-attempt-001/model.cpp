#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Set covering: hire the cheapest crew such that every task has at least one
// qualified worker on it.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int nb_workers = instance.at("nb_workers").get<int>();
  const int num_tasks = instance.at("num_tasks").get<int>();
  const std::vector<int64_t> cost =
      instance.at("Cost").get<std::vector<int64_t>>();
  // Qualified is ragged: one list of qualified workers per task, 1-based.
  const json& qualified = instance.at("Qualified");

  std::vector<BoolVar> workers;
  for (int w = 0; w < nb_workers; ++w) workers.push_back(model.NewBoolVar());

  int64_t cost_sum = 0;
  for (const int64_t c : cost) cost_sum += c;
  // The reference declares total_cost over 0..nb_workers * sum(Cost).
  IntVar total_cost = model.NewIntVar(Domain(0, nb_workers * cost_sum));

  LinearExpr wage_bill;
  for (int w = 0; w < nb_workers; ++w) wage_bill += cost[w] * workers[w];
  model.AddEquality(total_cost, wage_bill);

  for (int j = 0; j < num_tasks; ++j) {
    LinearExpr staffed;
    for (const auto& entry : qualified.at(j)) {
      staffed += workers[entry.get<int>() - 1];
    }
    model.AddGreaterOrEqual(staffed, 1);
  }

  model.Minimize(total_cost);

  json out = json::array();
  for (const BoolVar& b : workers) out.push_back(b.index());
  outputs = {{"total_cost", total_cost.index()}, {"workers", out}};
}
