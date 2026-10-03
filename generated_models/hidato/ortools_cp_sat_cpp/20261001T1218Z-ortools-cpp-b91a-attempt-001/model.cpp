#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Hidato: fill a grid with the numbers 1..rows*cols, each used once, so that
// the given numbers stay where they are and consecutive numbers sit in cells
// that touch horizontally, vertically or diagonally.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  // puzzle[i][j] is a given number, or 0 for an empty cell.
  const std::vector<std::vector<int64_t>> puzzle =
      instance.at("puzzle").get<std::vector<std::vector<int64_t>>>();
  const int r = static_cast<int>(puzzle.size());
  const int c = static_cast<int>(puzzle[0].size());
  const int64_t last = static_cast<int64_t>(r) * c;

  // x[i][j] is the number written in row i, column j.
  std::vector<std::vector<IntVar>> x(r);
  std::vector<IntVar> all_cells;
  for (int i = 0; i < r; ++i) {
    for (int j = 0; j < c; ++j) {
      x[i].push_back(model.NewIntVar(Domain(1, last)));
      all_cells.push_back(x[i][j]);
    }
  }

  // Each number is used exactly once.
  model.AddAllDifferent(all_cells);

  // The numbers given at the start stay where they are.
  for (int i = 0; i < r; ++i)
    for (int j = 0; j < c; ++j)
      if (puzzle[i][j] > 0) model.AddEquality(x[i][j], puzzle[i][j]);

  // Consecutive numbers touch. The reference looks up the cell of k and the
  // cell of k+1; here the same condition is stated from each cell: unless the
  // cell holds the last number, one of its (up to eight) neighbouring cells
  // holds the number one higher. With all numbers different, this makes
  // 1, 2, ..., rows*cols a chain of touching cells.
  for (int i = 0; i < r; ++i) {
    for (int j = 0; j < c; ++j) {
      std::vector<BoolVar> options;
      for (int a = -1; a <= 1; ++a) {
        for (int b = -1; b <= 1; ++b) {
          if (a == 0 && b == 0) continue;  // a cell is not its own neighbour
          const int ni = i + a, nj = j + b;
          if (ni < 0 || ni >= r || nj < 0 || nj >= c) continue;  // stay inside the grid
          const BoolVar next_is_here = model.NewBoolVar();
          model.AddEquality(x[ni][nj], x[i][j] + 1).OnlyEnforceIf(next_is_here);
          options.push_back(next_is_here);
        }
      }
      // is_last may only be true for the cell that holds the largest number.
      const BoolVar is_last = model.NewBoolVar();
      model.AddEquality(x[i][j], last).OnlyEnforceIf(is_last);
      options.push_back(is_last);
      model.AddBoolOr(options);
    }
  }

  json out = json::array();
  for (int i = 0; i < r; ++i) {
    json row = json::array();
    for (int j = 0; j < c; ++j) row.push_back(x[i][j].index());
    out.push_back(row);
  }
  outputs = {{"x", out}};
}
