#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Network assignment: spend each person's hours in full, meet each project's
// demand exactly, respect the per-pair capacity, and pay as little as possible.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<int64_t> supply =
      instance.at("supply").get<std::vector<int64_t>>();
  const std::vector<int64_t> demand =
      instance.at("demand").get<std::vector<int64_t>>();
  const std::vector<std::vector<int64_t>> cost =
      instance.at("cost").get<std::vector<std::vector<int64_t>>>();
  const std::vector<std::vector<int64_t>> limit =
      instance.at("limit").get<std::vector<std::vector<int64_t>>>();
  const int num_people = static_cast<int>(supply.size());
  const int num_projects = static_cast<int>(demand.size());

  // Hours per pair keep the reference's declared 0..10 domain.
  std::vector<std::vector<IntVar>> assign(num_people);
  for (int i = 0; i < num_people; ++i) {
    for (int j = 0; j < num_projects; ++j) {
      assign[i].push_back(model.NewIntVar(Domain(0, 10)));
      model.AddLessOrEqual(assign[i][j], limit[i][j]);
    }
  }

  for (int i = 0; i < num_people; ++i) {
    LinearExpr row;
    for (int j = 0; j < num_projects; ++j) row += assign[i][j];
    model.AddEquality(row, supply[i]);
  }
  for (int j = 0; j < num_projects; ++j) {
    LinearExpr col;
    for (int i = 0; i < num_people; ++i) col += assign[i][j];
    model.AddEquality(col, demand[j]);
  }

  int64_t cost_bound = 0;
  LinearExpr spend;
  for (int i = 0; i < num_people; ++i) {
    for (int j = 0; j < num_projects; ++j) {
      spend += cost[i][j] * assign[i][j];
      cost_bound += 10 * cost[i][j];
    }
  }
  IntVar total_cost = model.NewIntVar(Domain(0, cost_bound));
  model.AddEquality(total_cost, spend);
  model.Minimize(total_cost);

  json out = json::array();
  for (int i = 0; i < num_people; ++i) {
    json r = json::array();
    for (int j = 0; j < num_projects; ++j) r.push_back(assign[i][j].index());
    out.push_back(r);
  }
  outputs = {{"assign", out}, {"total_cost", total_cost.index()}};
}
