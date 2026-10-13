// Flow Free: connect matching colours with pipes so that every cell of the board is covered
// and pipes of different colours do not cross or overlap.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  auto board = instance.at("board").get<std::vector<std::vector<int>>>();
  int R = static_cast<int>(board.size());
  int C = static_cast<int>(board[0].size());
  int colours = 0;
  for (auto& row : board) for (int v : row) colours = std::max(colours, v);

  // B[i][j] is the colour of cell (i, j); the cells with a value of 0 need a colour
  vec<vec<IntVar*>> B;
  createVars(B, R, C, 1, colours, true);

  // the given cells keep their colour
  for (int i = 0; i < R; ++i)
    for (int j = 0; j < C; ++j)
      if (board[i][j] != 0) int_rel(B[i][j], IRT_EQ, board[i][j]);

  // Pipes are paths: an end point (a given cell) touches exactly one cell of its own colour
  // and every other cell lies in the middle of a pipe, touching exactly two cells of its
  // own colour.
  const int di[4] = {-1, 1, 0, 0};
  const int dj[4] = {0, 0, -1, 1};
  for (int i = 0; i < R; ++i)
    for (int j = 0; j < C; ++j) {
      vec<BoolView> same;
      for (int d = 0; d < 4; ++d) {
        int a = i + di[d], b = j + dj[d];
        if (a < 0 || b < 0 || a >= R || b >= C) continue;
        BoolView s = newBoolVar();
        int_rel_reif(B[i][j], IRT_EQ, B[a][b], s);  // s <-> neighbour has the same colour
        same.push(s);
      }
      int want = board[i][j] != 0 ? 1 : 2;
      bool_linear(same, IRT_EQ, getConstant(want));
    }

  vec<IntVar*> cells;
  flatten(B, cells);
  branch(cells, VAR_INORDER, VAL_MIN);

  json rows = json::array();
  for (int i = 0; i < R; ++i) {
    json row = json::array();
    for (int j = 0; j < C; ++j) row.push_back(dcp::out(B[i][j]));
    rows.push_back(row);
  }
  outputs = {{"B", rows}};
}
