// Maximum density still life: on an n x m active grid of Conway's Game of Life, find the
// stable pattern with the most live cells. Cells outside the grid are dead.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");
  int m = instance.at("m");

  // grid[i][j] = 1 if the cell in row i, column j of the active grid is alive
  vec<vec<IntVar*>> grid;
  createVars(grid, n, m, 0, 1, true);

  // cell(i, j) for the whole board: cells outside the active grid are dead
  IntVar* dead = getConstant(0);
  auto cell = [&](int i, int j) -> IntVar* {
    if (i < 0 || j < 0 || i >= n || j >= m) return dead;
    return grid[i][j];
  };

  // the number of live neighbours of cell (i, j), for the active grid and the ring of cells
  // just outside it (cells further out cannot have live neighbours)
  auto neighbours = [&](int i, int j) -> IntVar* {
    vec<IntVar*> nb;
    for (int di = -1; di <= 1; ++di)
      for (int dj = -1; dj <= 1; ++dj)
        if ((di != 0 || dj != 0) && cell(i + di, j + dj) != dead) nb.push(cell(i + di, j + dj));
    IntVar* s = newIntVar(0, 8);
    if (nb.size() == 0) { int_rel(s, IRT_EQ, 0); return s; }
    int_linear(nb, IRT_EQ, s);
    return s;
  };

  // A live cell must have exactly 2 or 3 live neighbours to remain alive; a dead cell must
  // not have exactly 3 live neighbours. Tuples (cell, number of live neighbours) allowed:
  vec<vec<int>> allowed;
  for (int s = 0; s <= 8; ++s) {
    bool alive_ok = (s == 2 || s == 3);
    bool dead_ok = (s != 3);
    if (alive_ok) { allowed.push(); allowed.last().push(1); allowed.last().push(s); }
    if (dead_ok) { allowed.push(); allowed.last().push(0); allowed.last().push(s); }
  }
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < m; ++j) {
      vec<IntVar*> pair;
      pair.push(grid[i][j]);
      pair.push(neighbours(i, j));
      table(pair, allowed);
    }

  // a dead cell just outside the active grid must not have exactly 3 live neighbours
  for (int i = -1; i <= n; ++i)
    for (int j = -1; j <= m; ++j) {
      if (i >= 0 && i < n && j >= 0 && j < m) continue;
      IntVar* s = neighbours(i, j);
      int_rel(s, IRT_NE, 3);
    }

  // maximize the number of live cells in the active grid
  vec<IntVar*> flat;
  flatten(grid, flat);
  IntVar* live = newIntVar(0, n * m);
  int_linear(flat, IRT_EQ, live);

  branch(flat, VAR_INORDER, VAL_MAX);
  optimize(live, OPT_MAX);

  json rows = json::array();
  for (int i = 0; i < n; ++i) {
    json row = json::array();
    for (int j = 0; j < m; ++j) row.push_back(dcp::out(grid[i][j]));
    rows.push_back(row);
  }
  outputs = {{"grid", rows}};
}
