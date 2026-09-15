#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Assignment costs: every task goes to exactly one person and no person takes
// two tasks, at minimum total cost.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<std::vector<int64_t>> cost =
      instance.at("cost").get<std::vector<std::vector<int64_t>>>();
  const int rows = static_cast<int>(cost.size());
  const int cols = rows == 0 ? 0 : static_cast<int>(cost[0].size());

  std::vector<std::vector<BoolVar>> x(rows);
  int64_t max_cost = 0;
  for (int i = 0; i < rows; ++i) {
    for (int j = 0; j < cols; ++j) {
      x[i].push_back(model.NewBoolVar());
      max_cost += cost[i][j];
    }
  }

  LinearExpr spend;
  for (int i = 0; i < rows; ++i) {
    for (int j = 0; j < cols; ++j) spend += cost[i][j] * x[i][j];
  }
  IntVar total_cost = model.NewIntVar(Domain(0, max_cost));
  model.AddEquality(total_cost, spend);

  // Exactly one assignment per task; at most one per person.
  for (int i = 0; i < rows; ++i) {
    LinearExpr row;
    for (int j = 0; j < cols; ++j) row += x[i][j];
    model.AddEquality(row, 1);
  }
  for (int j = 0; j < cols; ++j) {
    LinearExpr col;
    for (int i = 0; i < rows; ++i) col += x[i][j];
    model.AddLessOrEqual(col, 1);
  }

  model.Minimize(total_cost);

  json out = json::array();
  for (int i = 0; i < rows; ++i) {
    json r = json::array();
    for (int j = 0; j < cols; ++j) r.push_back(x[i][j].index());
    out.push_back(r);
  }
  outputs = {{"x", out}};
}
