// Hidato: fill the grid with the numbers 1..(rows*cols) so that consecutive numbers touch
// horizontally, vertically or diagonally; some numbers are given.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  auto puzzle = instance.at("puzzle").get<std::vector<std::vector<int>>>();
  int R = static_cast<int>(puzzle.size());
  int C = static_cast<int>(puzzle[0].size());
  int N = R * C;

  // x[i][j] is the number in cell (i, j); every cell holds one of 1..N
  vec<vec<IntVar*>> x;
  createVars(x, R, C, 1, N);
  vec<IntVar*> cells;  // row-major, cell index = i * C + j
  flatten(x, cells);

  // the numbers already given in the puzzle stay where they are (0 marks an empty cell)
  for (int i = 0; i < R; ++i)
    for (int j = 0; j < C; ++j)
      if (puzzle[i][j] != 0) int_rel(x[i][j], IRT_EQ, puzzle[i][j]);

  // each number is used exactly once
  all_different(cells);

  // pos[k-1] is the cell index where number k is written (the inverse of x)
  vec<IntVar*> pos;
  createVars(pos, N, 0, N - 1);
  all_different(pos);
  for (int k = 1; k <= N; ++k) array_var_int_element_bound(pos[k - 1], cells, getConstant(k));
  for (int i = 0; i < R; ++i)
    for (int j = 0; j < C; ++j)
      if (puzzle[i][j] != 0) int_rel(pos[puzzle[i][j] - 1], IRT_EQ, i * C + j);

  // consecutive numbers touch horizontally, vertically or diagonally
  vec<vec<int>> touching;
  for (int i = 0; i < R; ++i)
    for (int j = 0; j < C; ++j)
      for (int di = -1; di <= 1; ++di)
        for (int dj = -1; dj <= 1; ++dj) {
          int a = i + di, b = j + dj;
          if ((di == 0 && dj == 0) || a < 0 || b < 0 || a >= R || b >= C) continue;
          touching.push();
          touching.last().push(i * C + j);
          touching.last().push(a * C + b);
        }
  for (int k = 0; k + 1 < N; ++k) {
    vec<IntVar*> pair;
    pair.push(pos[k]);
    pair.push(pos[k + 1]);
    table(pair, touching);
  }

  // follow the path from number 1 onwards
  branch(pos, VAR_INORDER, VAL_MIN);

  json rows = json::array();
  for (int i = 0; i < R; ++i) {
    json row = json::array();
    for (int j = 0; j < C; ++j) row.push_back(dcp::out(x[i][j]));
    rows.push_back(row);
  }
  outputs = {{"x", rows}};
}
