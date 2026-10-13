// Futoshiki: fill an n x n grid with the digits 1..n so that every row and column holds each digit once,
// the given digits are kept, and the inequality signs between neighbouring cells hold.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<std::vector<int>> given = instance.at("values").get<std::vector<std::vector<int>>>();
  std::vector<std::vector<int>> lt = instance.at("lt").get<std::vector<std::vector<int>>>();
  int n = static_cast<int>(given.size());

  // grid[r][c] is the digit in row r, column c (0-based here; the instance uses 1-based coordinates for the inequalities)
  vec<vec<IntVar*>> grid;
  createVars(grid, n, n, 1, n);

  // every row contains each digit exactly once
  for (int r = 0; r < n; ++r) {
    vec<IntVar*> row;
    for (int c = 0; c < n; ++c) row.push(grid[r][c]);
    all_different(row);
  }

  // every column contains each digit exactly once
  for (int c = 0; c < n; ++c) {
    vec<IntVar*> col;
    for (int r = 0; r < n; ++r) col.push(grid[r][c]);
    all_different(col);
  }

  // the digits given at the start of the puzzle stay where they are (0 marks an empty cell)
  for (int r = 0; r < n; ++r) {
    for (int c = 0; c < n; ++c) {
      if (given[r][c] != 0) int_rel(grid[r][c], IRT_EQ, given[r][c]);
    }
  }

  // each inequality is [r1, c1, r2, c2] meaning the digit at (r1, c1) is smaller than the digit at (r2, c2)
  for (const auto& e : lt) {
    int_rel(grid[e[0] - 1][e[1] - 1], IRT_LT, grid[e[2] - 1][e[3] - 1]);
  }

  // search on the cells in reading order
  vec<IntVar*> cells;
  flatten(grid, cells);
  branch(cells, VAR_SIZE_MIN, VAL_MIN);

  json rows = json::array();
  for (int r = 0; r < n; ++r) {
    json row = json::array();
    for (int c = 0; c < n; ++c) row.push_back(dcp::out(grid[r][c]));
    rows.push_back(row);
  }
  outputs = {{"grid", rows}};
}
