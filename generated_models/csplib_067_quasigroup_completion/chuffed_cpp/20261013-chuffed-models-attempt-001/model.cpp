// Quasigroup completion: fill the empty cells of an N x N table so that every row and every
// column contains each of the values 1..N exactly once, keeping the given entries.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("N");
  std::vector<std::vector<int>> start = instance.at("start").get<std::vector<std::vector<int>>>();

  // cell[i][j] is the value in row i, column j (values 1..N)
  vec<vec<IntVar*>> cell;
  createVars(cell, n, n, 1, n);

  // the given entries of the table are fixed; a 0 in the instance marks an empty cell
  for (int i = 0; i < n; ++i) {
    for (int j = 0; j < n; ++j) {
      if (start[i][j] != 0) {
        // the given value stays in its cell
        int_rel(cell[i][j], IRT_EQ, start[i][j]);
      }
    }
  }

  // every row contains each value once
  for (int i = 0; i < n; ++i) {
    vec<IntVar*> row;
    for (int j = 0; j < n; ++j) row.push(cell[i][j]);
    all_different(row);
  }

  // every column contains each value once
  for (int j = 0; j < n; ++j) {
    vec<IntVar*> col;
    for (int i = 0; i < n; ++i) col.push(cell[i][j]);
    all_different(col);
  }

  // search over the table in reading order
  vec<IntVar*> flat;
  flatten(cell, flat);
  branch(flat, VAR_INORDER, VAL_MIN);

  json table = json::array();
  for (int i = 0; i < n; ++i) {
    json row = json::array();
    for (int j = 0; j < n; ++j) row.push_back(dcp::out(cell[i][j]));
    table.push_back(row);
  }
  outputs = {{"puzzle", table}};
}
