// Heterosquare: an n x n square x of the distinct integers 1..n^2 such that the
// sums of the rows, the columns and the two diagonals are all different.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int n = instance.at("n").get<int>();
  const int cells = n * n;  // the elements are the integers 1..cells

  // Every line sum lies in [n, n*cells], so any difference of two line sums is at most
  // n*cells - n in absolute value. M = n*cells - n + 1 is a valid big-M for the
  // "these two sums differ" rows, computed from the instance size.
  const double M = static_cast<double>(n) * cells - n + 1;

  // Cell (i, j) takes one value: y[i][j][v] is 1 when the element at (i, j) equals v + 1.
  std::vector<std::vector<std::vector<dcp::Lin>>> y(
      n, std::vector<std::vector<dcp::Lin>>(n, std::vector<dcp::Lin>(cells)));
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j)
      for (int v = 0; v < cells; ++v) y[i][j][v] = dcp::new_var(h, 0, 1);

  // The element at (i, j) is the value it is set to: x[i][j] = sum_v (v + 1) y[i][j][v].
  std::vector<std::vector<dcp::Lin>> x(n, std::vector<dcp::Lin>(n));
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) {
      dcp::Lin value;
      for (int v = 0; v < cells; ++v) value = value + static_cast<double>(v + 1) * y[i][j][v];
      x[i][j] = value;
    }

  // each cell holds exactly one value
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) {
      dcp::Lin one_value;
      for (int v = 0; v < cells; ++v) one_value = one_value + y[i][j][v];
      dcp::add_row(h, one_value, 1, 1);
    }

  // the elements are distinct: each value 1..n^2 is used by exactly one cell
  // (n^2 distinct values from 1..n^2 fill the square)
  for (int v = 0; v < cells; ++v) {
    dcp::Lin used;
    for (int i = 0; i < n; ++i)
      for (int j = 0; j < n; ++j) used = used + y[i][j][v];
    dcp::add_row(h, used, 1, 1);
  }

  // the line sums: each row, each column, and the two diagonals
  std::vector<dcp::Lin> sums;
  for (int i = 0; i < n; ++i) {
    dcp::Lin row_sum;
    for (int j = 0; j < n; ++j) row_sum = row_sum + x[i][j];
    sums.push_back(row_sum);
  }
  for (int j = 0; j < n; ++j) {
    dcp::Lin col_sum;
    for (int i = 0; i < n; ++i) col_sum = col_sum + x[i][j];
    sums.push_back(col_sum);
  }
  dcp::Lin diagonal, anti_diagonal;
  for (int i = 0; i < n; ++i) {
    diagonal = diagonal + x[i][i];
    anti_diagonal = anti_diagonal + x[i][n - 1 - i];
  }
  sums.push_back(diagonal);
  sums.push_back(anti_diagonal);

  // the sums are all different: for every pair of line sums a and b, a binary z says
  // which one is smaller, so the two sums cannot be equal
  for (size_t a = 0; a < sums.size(); ++a)
    for (size_t b = a + 1; b < sums.size(); ++b) {
      dcp::Lin z = dcp::new_var(h, 0, 1);
      // sum a + 1 <= sum b when z = 0
      dcp::add_row(h, sums[a] - sums[b] - M * z, -kHighsInf, -1);
      // sum b + 1 <= sum a when z = 1
      dcp::add_row(h, sums[b] - sums[a] + M * z, -kHighsInf, M - 1);
    }

  // the square is the output x; the problem is satisfaction, so there is no objective
  out.add("x", x);
}
