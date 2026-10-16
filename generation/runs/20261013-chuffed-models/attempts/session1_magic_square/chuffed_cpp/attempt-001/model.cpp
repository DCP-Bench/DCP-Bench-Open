// Magic square: an n x n grid of different integers 1..n^2 with equal row, column and diagonal sums.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");
  int cells = n * n;
  // the common sum is n(n^2+1)/2, as given in the problem statement
  int magic = n * (cells + 1) / 2;

  // square[r][c] is the integer in that cell
  vec<vec<IntVar*>> square;
  createVars(square, n, n, 1, cells);
  vec<IntVar*> flat;
  flatten(square, flat);

  // each cell contains a different integer from 1 to n^2
  all_different(flat);

  // the sum of the integers in each row is the magic sum
  for (int r = 0; r < n; ++r) int_linear(square[r], IRT_EQ, magic);

  // the sum of the integers in each column is the magic sum
  for (int c = 0; c < n; ++c) {
    vec<IntVar*> col;
    for (int r = 0; r < n; ++r) col.push(square[r][c]);
    int_linear(col, IRT_EQ, magic);
  }

  // the sum of the integers in each of the two diagonals is the magic sum
  vec<IntVar*> diag, anti;
  for (int i = 0; i < n; ++i) {
    diag.push(square[i][i]);
    anti.push(square[i][n - 1 - i]);
  }
  int_linear(diag, IRT_EQ, magic);
  int_linear(anti, IRT_EQ, magic);

  branch(flat, VAR_SIZE_MIN, VAL_MIN);
  json rows = json::array();
  for (int r = 0; r < n; ++r) {
    json row = json::array();
    for (int c = 0; c < n; ++c) row.push_back(dcp::out(square[r][c]));
    rows.push_back(row);
  }
  outputs = {{"square", rows}};
}
