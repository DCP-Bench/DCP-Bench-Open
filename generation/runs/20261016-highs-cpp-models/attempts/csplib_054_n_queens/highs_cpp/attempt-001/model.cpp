// N-queens: place n queens on an n x n chessboard so that no two queens attack each other.
// queens[i] is the column (1..n) of the queen in row i.
#include <cstdlib>

#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n").get<int>();

  // queens[i] is the column of the queen in row i, a number from 1 to n
  std::vector<dcp::Lin> queens;
  for (int i = 0; i < n; ++i) queens.push_back(dcp::new_var(h, 1, n));

  // y[i][v-1] = 1 when the queen of row i stands in column v
  std::vector<std::vector<dcp::Lin>> y(n, std::vector<dcp::Lin>(n));
  for (int i = 0; i < n; ++i)
    for (int v = 0; v < n; ++v) y[i][v] = dcp::new_var(h, 0, 1);

  // each row holds exactly one queen, and its column is the chosen column
  for (int i = 0; i < n; ++i) {
    // the queen of row i stands in exactly one column
    dcp::Lin one_column;
    dcp::Lin column_of_queen;
    for (int v = 1; v <= n; ++v) {
      one_column = one_column + y[i][v - 1];
      column_of_queen = column_of_queen + static_cast<double>(v) * y[i][v - 1];
    }
    dcp::add_row(h, one_column, 1, 1);
    // queens[i] is that column
    dcp::add_row(h, queens[i] - column_of_queen, 0, 0);
  }

  // no two queens share a column: each column holds at most one queen
  for (int v = 1; v <= n; ++v) {
    dcp::Lin in_column;
    for (int i = 0; i < n; ++i) in_column = in_column + y[i][v - 1];
    dcp::add_row(h, in_column, -kHighsInf, 1);
  }

  // binary b puts the difference d above the value v when b = 1, below it when b = 0,
  // so the pair "d is not v" holds. d ranges over -(n-1)..(n-1), so M = (n-1) + |v| + 1
  // from the board size covers both sides.
  auto differs_from = [&](const dcp::Lin& d, int v) {
    dcp::Lin b = dcp::new_var(h, 0, 1);
    double big_m = (n - 1) + std::abs(v) + 1;
    dcp::add_row(h, d - big_m * b, v + 1 - big_m, v - 1);
  };

  // no two queens share a diagonal: for rows i < j the column difference is neither
  // j - i nor i - j
  for (int i = 0; i < n; ++i) {
    for (int j = i + 1; j < n; ++j) {
      int gap = j - i;
      differs_from(queens[i] - queens[j], gap);
      differs_from(queens[i] - queens[j], -gap);
    }
  }

  out.add("queens", queens);
}
