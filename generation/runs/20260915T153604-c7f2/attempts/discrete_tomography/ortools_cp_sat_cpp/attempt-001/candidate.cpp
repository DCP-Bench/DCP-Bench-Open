#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Discrete tomography: reconstruct a 0/1 picture from its row and column sums.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<int64_t> row_sums =
      instance.at("row_sums").get<std::vector<int64_t>>();
  const std::vector<int64_t> col_sums =
      instance.at("col_sums").get<std::vector<int64_t>>();
  const int r = static_cast<int>(row_sums.size());
  const int c = static_cast<int>(col_sums.size());

  std::vector<std::vector<IntVar>> matrix(r);
  for (int i = 0; i < r; ++i) {
    for (int j = 0; j < c; ++j) {
      matrix[i].push_back(model.NewIntVar(Domain(0, 1)));
    }
  }

  for (int i = 0; i < r; ++i) {
    LinearExpr row;
    for (int j = 0; j < c; ++j) row += matrix[i][j];
    model.AddEquality(row, row_sums[i]);
  }
  for (int j = 0; j < c; ++j) {
    LinearExpr col;
    for (int i = 0; i < r; ++i) col += matrix[i][j];
    model.AddEquality(col, col_sums[j]);
  }

  json out = json::array();
  for (int i = 0; i < r; ++i) {
    json row = json::array();
    for (int j = 0; j < c; ++j) row.push_back(matrix[i][j].index());
    out.push_back(row);
  }
  outputs = {{"matrix", out}};
}
