// Minesweeper: decide which unopened cells contain a mine, given the numbers on the opened cells.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // the marker in game_data for an unopened cell (the instance uses -1)
  int unopened = instance.at("X");
  std::vector<std::vector<int>> game = instance.at("game_data").get<std::vector<std::vector<int>>>();
  int rows = static_cast<int>(game.size());
  int cols = static_cast<int>(game[0].size());

  // mine[i][j] = 1 if the cell in row i, column j holds a mine
  vec<vec<IntVar*>> mine;
  createVars(mine, rows, cols, 0, 1, true);

  // an opened cell cannot hold a mine
  for (int i = 0; i < rows; ++i) {
    for (int j = 0; j < cols; ++j) {
      if (game[i][j] != unopened) {
        // the opened cell at row i, column j is safe
        int_rel(mine[i][j], IRT_EQ, 0);
      }
    }
  }

  // each opened cell shows the number of mines among its up to eight neighbours
  for (int i = 0; i < rows; ++i) {
    for (int j = 0; j < cols; ++j) {
      if (game[i][j] == unopened) continue;
      // the neighbours of the opened cell at row i, column j
      vec<IntVar*> around;
      for (int di = -1; di <= 1; ++di) {
        for (int dj = -1; dj <= 1; ++dj) {
          if (di == 0 && dj == 0) continue;
          int r = i + di, c = j + dj;
          if (r < 0 || r >= rows || c < 0 || c >= cols) continue;
          around.push(mine[r][c]);
        }
      }
      // the number of mines around the cell equals the number shown on it
      int_linear(around, IRT_EQ, game[i][j]);
    }
  }

  // search over the cells in reading order
  vec<IntVar*> flat;
  flatten(mine, flat);
  branch(flat, VAR_INORDER, VAL_MIN);

  json mines = json::array();
  for (int i = 0; i < rows; ++i) {
    json row = json::array();
    for (int j = 0; j < cols; ++j) row.push_back(dcp::out(mine[i][j]));
    mines.push_back(row);
  }
  outputs = {{"mines", mines}};
}
