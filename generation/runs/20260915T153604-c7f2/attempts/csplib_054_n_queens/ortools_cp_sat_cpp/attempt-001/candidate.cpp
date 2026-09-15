#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// N queens: one queen per row, no two sharing a column or a diagonal.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();

  std::vector<IntVar> queens;
  for (int i = 0; i < n; ++i) queens.push_back(model.NewIntVar(Domain(1, n)));

  std::vector<LinearExpr> columns;
  std::vector<LinearExpr> down_diagonals;
  std::vector<LinearExpr> up_diagonals;
  for (int i = 0; i < n; ++i) {
    columns.push_back(queens[i]);
    down_diagonals.push_back(queens[i] - i);
    up_diagonals.push_back(queens[i] + i);
  }
  model.AddAllDifferent(columns);
  model.AddAllDifferent(down_diagonals);
  model.AddAllDifferent(up_diagonals);

  json out = json::array();
  for (const IntVar& q : queens) out.push_back(q.index());
  outputs = {{"queens", out}};
}
