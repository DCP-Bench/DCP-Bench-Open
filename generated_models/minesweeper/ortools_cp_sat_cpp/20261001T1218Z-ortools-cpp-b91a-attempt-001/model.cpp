#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Minesweeper: some cells are opened and show how many of their neighbouring
// cells hold a mine; the other cells are unopened (marked X). Decide which
// cells hold a mine.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  // X is the marker for a cell that is not opened.
  const int64_t X = instance.at("X").get<int64_t>();
  // game_data[r][c] is the number of mines around an opened cell, or X.
  const std::vector<std::vector<int64_t>> game_data =
      instance.at("game_data").get<std::vector<std::vector<int64_t>>>();
  const int rows = static_cast<int>(game_data.size());
  const int cols = static_cast<int>(game_data[0].size());

  // mines[r][c] is true when the cell holds a mine.
  std::vector<std::vector<BoolVar>> mines(rows);
  for (int r = 0; r < rows; ++r)
    for (int c = 0; c < cols; ++c) mines[r].push_back(model.NewBoolVar());

  for (int r = 0; r < rows; ++r) {
    for (int c = 0; c < cols; ++c) {
      if (game_data[r][c] == X) continue;  // an unopened cell is unconstrained
      // An opened cell is not a mine.
      model.AddEquality(mines[r][c], 0);
      // Its number is the count of mines among its (up to eight) neighbours.
      LinearExpr neighbour_mines;
      for (int a = -1; a <= 1; ++a) {
        for (int b = -1; b <= 1; ++b) {
          if (a == 0 && b == 0) continue;
          const int nr = r + a, nc = c + b;
          if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) continue;  // off the board
          neighbour_mines += mines[nr][nc];
        }
      }
      model.AddEquality(neighbour_mines, game_data[r][c]);
    }
  }

  json out = json::array();
  for (int r = 0; r < rows; ++r) {
    json row = json::array();
    for (int c = 0; c < cols; ++c) row.push_back(mines[r][c].index());
    out.push_back(row);
  }
  outputs = {{"mines", out}};
}
