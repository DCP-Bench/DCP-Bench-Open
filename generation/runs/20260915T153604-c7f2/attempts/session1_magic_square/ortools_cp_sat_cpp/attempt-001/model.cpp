#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Magic square: place 1..n^2 so that every row, column and both diagonals add
// up to the same total.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();
  // The magic constant follows from n alone.
  const int64_t magic_sum = int64_t{n} * (int64_t{n} * n + 1) / 2;

  std::vector<std::vector<IntVar>> square(n);
  std::vector<IntVar> all_cells;
  for (int i = 0; i < n; ++i) {
    for (int j = 0; j < n; ++j) {
      square[i].push_back(model.NewIntVar(Domain(1, int64_t{n} * n)));
      all_cells.push_back(square[i][j]);
    }
  }
  model.AddAllDifferent(all_cells);

  for (int i = 0; i < n; ++i) {
    LinearExpr row;
    LinearExpr col;
    for (int j = 0; j < n; ++j) {
      row += square[i][j];
      col += square[j][i];
    }
    model.AddEquality(row, magic_sum);
    model.AddEquality(col, magic_sum);
  }

  LinearExpr main_diagonal;
  LinearExpr anti_diagonal;
  for (int i = 0; i < n; ++i) {
    main_diagonal += square[i][i];
    anti_diagonal += square[i][n - 1 - i];
  }
  model.AddEquality(main_diagonal, magic_sum);
  model.AddEquality(anti_diagonal, magic_sum);

  json out = json::array();
  for (int i = 0; i < n; ++i) {
    json row = json::array();
    for (int j = 0; j < n; ++j) row.push_back(square[i][j].index());
    out.push_back(row);
  }
  outputs = {{"square", out}};
}
