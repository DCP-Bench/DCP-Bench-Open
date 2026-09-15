#include <cmath>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Sudoku: fill the grid so rows, columns and blocks each hold every digit
// once, keeping the given cells.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<std::vector<int64_t>> given =
      instance.at("input_grid").get<std::vector<std::vector<int64_t>>>();
  const int n = static_cast<int>(given.size());
  // Blocks are the square sub-grids, so their side is the square root of the
  // grid size; zero marks an empty cell, as in the reference.
  const int block = static_cast<int>(std::lround(std::sqrt(n)));
  const int64_t empty = 0;

  std::vector<std::vector<IntVar>> grid(n);
  for (int i = 0; i < n; ++i) {
    for (int j = 0; j < n; ++j) grid[i].push_back(model.NewIntVar(Domain(1, n)));
  }

  for (int i = 0; i < n; ++i) {
    for (int j = 0; j < n; ++j) {
      if (given[i][j] != empty) model.AddEquality(grid[i][j], given[i][j]);
    }
  }

  for (int i = 0; i < n; ++i) {
    std::vector<IntVar> row;
    std::vector<IntVar> col;
    for (int j = 0; j < n; ++j) {
      row.push_back(grid[i][j]);
      col.push_back(grid[j][i]);
    }
    model.AddAllDifferent(row);
    model.AddAllDifferent(col);
  }

  for (int i = 0; i < n; i += block) {
    for (int j = 0; j < n; j += block) {
      std::vector<IntVar> cells;
      for (int di = 0; di < block; ++di) {
        for (int dj = 0; dj < block; ++dj) cells.push_back(grid[i + di][j + dj]);
      }
      model.AddAllDifferent(cells);
    }
  }

  json out = json::array();
  for (int i = 0; i < n; ++i) {
    json row = json::array();
    for (int j = 0; j < n; ++j) row.push_back(grid[i][j].index());
    out.push_back(row);
  }
  outputs = {{"grid", out}};
}
