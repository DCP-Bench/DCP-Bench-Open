// Killer sudoku: fill the grid with 1..9 so that rows, columns and boxes are all different and every cage sums to its target with no repeated digit.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");
  int box = 1;
  while (box * box < n) ++box;

  // x[r][c] is the digit in row r, column c
  vec<vec<IntVar*>> x;
  createVars(x, n, n, 1, n, true);

  // each row contains each number exactly once
  for (int r = 0; r < n; ++r) all_different(x[r]);

  // each column contains each number exactly once
  vec<vec<IntVar*>> cols;
  transpose(x, cols);
  for (int c = 0; c < n; ++c) all_different(cols[c]);

  // each box (nonet) contains each number exactly once
  for (int br = 0; br < n; br += box)
    for (int bc = 0; bc < n; bc += box) {
      vec<IntVar*> cells;
      for (int r = br; r < br + box; ++r)
        for (int c = bc; c < bc + box; ++c) cells.push(x[r][c]);
      all_different(cells);
    }

  // problem is a list of cages [sum, [[row, col], ...]] with 1-based cell coordinates
  // the sum of all numbers in a cage must match its target, and no number appears twice in a cage
  for (const json& cage : instance.at("problem")) {
    int target = cage[0];
    vec<IntVar*> cells;
    for (const json& cell : cage[1]) {
      int r = cell[0].get<int>() - 1;
      int c = cell[1].get<int>() - 1;
      cells.push(x[r][c]);
    }
    int_linear(cells, IRT_EQ, target);
    all_different(cells);
  }

  vec<IntVar*> flat;
  flatten(x, flat);
  branch(flat, VAR_SIZE_MIN, VAL_MIN);

  json grid = json::array();
  for (int r = 0; r < n; ++r) {
    json row = json::array();
    for (int c = 0; c < n; ++c) row.push_back(dcp::out(x[r][c]));
    grid.push_back(row);
  }
  outputs = {{"x", grid}};
}
