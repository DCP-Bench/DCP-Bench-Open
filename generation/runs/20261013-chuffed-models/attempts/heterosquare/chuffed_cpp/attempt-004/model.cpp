// Heterosquare: fill an n x n square with the distinct integers 1..n^2 so that all of its
// row sums, column sums and two diagonal sums are different from each other.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");
  int cells_count = n * n;

  // x[i][j] is the entry in row i, column j
  vec<vec<IntVar*>> x;
  createVars(x, n, n, 1, cells_count);

  // the entries of the square are distinct integers from 1 to n^2
  vec<IntVar*> all;
  flatten(x, all);
  all_different(all);

  // the sums of the rows, the columns and the two diagonals, in that order
  // (a sum of n distinct entries from 1..n^2 lies between n(n+1)/2 and n^3)
  int lo = n * (n + 1) / 2;
  int hi = n * cells_count;
  vec<IntVar*> sums;

  // each row adds up to its sum
  for (int i = 0; i < n; ++i) {
    vec<IntVar*> row;
    for (int j = 0; j < n; ++j) row.push(x[i][j]);
    IntVar* s = newIntVar(lo, hi);
    int_linear(row, IRT_EQ, s);
    sums.push(s);
  }

  // each column adds up to its sum
  for (int j = 0; j < n; ++j) {
    vec<IntVar*> col;
    for (int i = 0; i < n; ++i) col.push(x[i][j]);
    IntVar* s = newIntVar(lo, hi);
    int_linear(col, IRT_EQ, s);
    sums.push(s);
  }

  // the main diagonal adds up to its sum
  vec<IntVar*> diag, anti;
  for (int i = 0; i < n; ++i) {
    diag.push(x[i][i]);
    anti.push(x[i][n - 1 - i]);
  }
  IntVar* d1 = newIntVar(lo, hi);
  int_linear(diag, IRT_EQ, d1);
  sums.push(d1);

  // the anti-diagonal adds up to its sum
  IntVar* d2 = newIntVar(lo, hi);
  int_linear(anti, IRT_EQ, d2);
  sums.push(d2);

  // all row, column and diagonal sums are different
  all_different(sums);

  // search over the entries of the square in reading order
  branch(all, VAR_INORDER, VAL_MIN);

  json square = json::array();
  for (int i = 0; i < n; ++i) {
    json row = json::array();
    for (int j = 0; j < n; ++j) row.push_back(dcp::out(x[i][j]));
    square.push_back(row);
  }
  outputs = {{"x", square}};
}
