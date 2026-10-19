// Futoshiki: an n x n grid, each cell holds a number 1..n. Each row and each column
// holds the numbers 1 to n exactly once. Some cells are given a number at the start.
// Some pairs of neighbouring cells carry an inequality sign, and the number in the
// first cell must be lower than the number in the second.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const json& values = instance.at("values");
  const json& lt = instance.at("lt");
  const int n = static_cast<int>(values.size());

  // the number in each cell, between 1 and n
  std::vector<std::vector<dcp::Lin>> grid(n, std::vector<dcp::Lin>(n));
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) grid[i][j] = dcp::new_var(h, 1, n);

  // y[i][j][v] = 1 when cell (i, j) holds the number v + 1
  std::vector<std::vector<std::vector<dcp::Lin>>> y(
      n, std::vector<std::vector<dcp::Lin>>(n, std::vector<dcp::Lin>(n)));
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j)
      for (int v = 0; v < n; ++v) y[i][j][v] = dcp::new_var(h, 0, 1);

  // every cell holds exactly one number
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) {
      dcp::Lin one;
      for (int v = 0; v < n; ++v) one = one + y[i][j][v];
      dcp::add_row(h, one, 1, 1);
    }

  // the cell value is the number chosen by its indicators
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) {
      dcp::Lin e = grid[i][j];
      for (int v = 0; v < n; ++v) e = e - static_cast<double>(v + 1) * y[i][j][v];
      dcp::add_row(h, e, 0, 0);
    }

  // every row holds each number 1 to n exactly once
  for (int i = 0; i < n; ++i)
    for (int v = 0; v < n; ++v) {
      dcp::Lin e;
      for (int j = 0; j < n; ++j) e = e + y[i][j][v];
      dcp::add_row(h, e, 1, 1);
    }

  // every column holds each number 1 to n exactly once
  for (int j = 0; j < n; ++j)
    for (int v = 0; v < n; ++v) {
      dcp::Lin e;
      for (int i = 0; i < n; ++i) e = e + y[i][j][v];
      dcp::add_row(h, e, 1, 1);
    }

  // a number given at the start stays in its cell
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) {
      int given = values[i][j].get<int>();
      if (given > 0) dcp::add_row(h, grid[i][j], given, given);
    }

  // an inequality sign: the first cell holds a lower number than the second cell
  // (the instance gives 1-based row and column numbers)
  for (const json& sign : lt) {
    int r1 = sign[0].get<int>() - 1, c1 = sign[1].get<int>() - 1;
    int r2 = sign[2].get<int>() - 1, c2 = sign[3].get<int>() - 1;
    dcp::add_row(h, grid[r1][c1] - grid[r2][c2], -kHighsInf, -1);
  }

  out.add("grid", grid);
}
