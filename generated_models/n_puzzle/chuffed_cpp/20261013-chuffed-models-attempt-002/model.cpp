// N-puzzle: find the sequence of board states from the start to the end configuration, sliding the blank one step per move.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n_steps = instance.at("N_STEPS");  // number of states, including start and end
  std::vector<std::vector<int>> start = instance.at("puzzle_start").get<std::vector<std::vector<int>>>();
  std::vector<std::vector<int>> end = instance.at("puzzle_end").get<std::vector<std::vector<int>>>();
  int R = static_cast<int>(start.size());
  int C = static_cast<int>(start[0].size());
  int cells = R * C;

  // cell[t][r*C+c] is the tile at row r, column c in state t (0 is the blank)
  vec<vec<IntVar*>> cell;
  createVars(cell, n_steps, cells, 0, cells - 1, true);
  // where[t][v] is the cell holding tile v in state t; it is the inverse of cell[t]
  vec<vec<IntVar*>> where;
  createVars(where, n_steps, cells, 0, cells - 1, true);

  // each state is a permutation of the tiles
  for (int t = 0; t < n_steps; ++t) inverse(cell[t], where[t]);

  // the first state is the start configuration and the last state is the end configuration
  for (int r = 0; r < R; ++r)
    for (int c = 0; c < C; ++c) {
      int_rel(cell[0][r * C + c], IRT_EQ, start[r][c]);
      int_rel(cell[n_steps - 1][r * C + c], IRT_EQ, end[r][c]);
    }

  // a move slides the blank to a neighbouring cell: its position (where[t][0]) changes to an adjacent cell
  vec<vec<int>> adjacent;
  for (int r = 0; r < R; ++r)
    for (int c = 0; c < C; ++c) {
      int p = r * C + c;
      if (r > 0) { adjacent.push(); adjacent.last().push(p); adjacent.last().push(p - C); }
      if (r + 1 < R) { adjacent.push(); adjacent.last().push(p); adjacent.last().push(p + C); }
      if (c > 0) { adjacent.push(); adjacent.last().push(p); adjacent.last().push(p - 1); }
      if (c + 1 < C) { adjacent.push(); adjacent.last().push(p); adjacent.last().push(p + 1); }
    }
  for (int t = 0; t + 1 < n_steps; ++t) {
    vec<IntVar*> blanks;
    blanks.push(where[t][0]);
    blanks.push(where[t + 1][0]);
    table(blanks, adjacent);  // adjacent cells, so the state changes at every step (no freezing)

    // only the blank and the tile it swaps with change: exactly two cells differ between consecutive states
    vec<IntVar*> changed;
    for (int p = 0; p < cells; ++p) {
      BoolView d = newBoolVar();
      int_rel_reif(cell[t][p], IRT_NE, cell[t + 1][p], d);
      IntVar* di = newIntVar(0, 1);
      bool2int(d, di);
      changed.push(di);
    }
    int_linear(changed, IRT_EQ, 2);
  }

  // the blank positions are the decision variables
  vec<IntVar*> blank_path;
  for (int t = 0; t < n_steps; ++t) blank_path.push(where[t][0]);
  branch(blank_path, VAR_INORDER, VAL_MIN);

  json steps = json::array();
  for (int t = 0; t < n_steps; ++t) {
    json grid = json::array();
    for (int r = 0; r < R; ++r) {
      json row = json::array();
      for (int c = 0; c < C; ++c) row.push_back(dcp::out(cell[t][r * C + c]));
      grid.push_back(row);
    }
    steps.push_back(grid);
  }
  outputs = {{"steps", steps}};
}
