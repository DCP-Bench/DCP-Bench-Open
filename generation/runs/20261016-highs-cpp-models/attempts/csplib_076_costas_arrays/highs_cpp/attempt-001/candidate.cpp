// csplib_076 Costas arrays: n marks on an n x n grid, one mark per row and one per
// column, such that the n(n-1)/2 difference vectors between the marks are all different.
// The model reads n from the instance. X_1..X_n is the permutation of 1..n (the column of
// the mark in each row), and the difference triangle has one line per length l = 1..n-1.
#include <vector>

#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int n = instance.at("n").get<int>();
  const int diffs = 2 * n - 1;  // differences X_i - X_j lie in -(n-1)..(n-1)

  // mark[i][v] = 1 when the mark of row i is in column v + 1, so X_i = v + 1.
  std::vector<std::vector<dcp::Lin>> mark(n, std::vector<dcp::Lin>(n));
  for (int i = 0; i < n; ++i)
    for (int v = 0; v < n; ++v) mark[i][v] = dcp::new_var(h, 0, 1);

  // X_i is the column of the mark in row i.
  std::vector<dcp::Lin> X(n);
  for (int i = 0; i < n; ++i)
    for (int v = 0; v < n; ++v) X[i] = X[i] + static_cast<double>(v + 1) * mark[i][v];

  // one mark per row
  for (int i = 0; i < n; ++i) {
    dcp::Lin row_sum;
    for (int v = 0; v < n; ++v) row_sum = row_sum + mark[i][v];
    dcp::add_row(h, row_sum, 1, 1);
  }

  // one mark per column: X_1..X_n is a permutation of 1..n
  for (int v = 0; v < n; ++v) {
    dcp::Lin col_sum;
    for (int i = 0; i < n; ++i) col_sum = col_sum + mark[i][v];
    dcp::add_row(h, col_sum, 1, 1);
  }

  // difference triangle: for each length l = 1..n-1, the differences X_i - X_{i+l}
  // (i = 1..n-l) form one line of the triangle
  for (int l = 1; l <= n - 1; ++l) {
    const int cells = n - l;
    // pick[i][k] = 1 when the difference X_i - X_{i+l} takes the value k - (n-1)
    std::vector<std::vector<dcp::Lin>> pick(cells, std::vector<dcp::Lin>(diffs));
    for (int i = 0; i < cells; ++i) {
      dcp::Lin one, value;
      for (int k = 0; k < diffs; ++k) {
        pick[i][k] = dcp::new_var(h, 0, 1);
        one = one + pick[i][k];
        value = value + static_cast<double>(k - (n - 1)) * pick[i][k];
      }
      // each cell of the line holds exactly one difference value
      dcp::add_row(h, one, 1, 1);
      // the cell is the difference X_i - X_{i+l}
      dcp::add_row(h, X[i] - X[i + l] - value, 0, 0);
    }
    // all different within the line: each difference value appears at most once
    for (int k = 0; k < diffs; ++k) {
      dcp::Lin used;
      for (int i = 0; i < cells; ++i) used = used + pick[i][k];
      dcp::add_row(h, used, -kHighsInf, 1);
    }
  }

  // print the permutation X_1..X_n, 1-based
  out.add("costas", X);
}
