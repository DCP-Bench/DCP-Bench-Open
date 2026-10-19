// csplib_067 quasigroup completion: complete a partially filled order N quasigroup,
// an N x N multiplication table in which each element from 1 to N occurs exactly once
// in every row and every column, and which agrees with the given cells (0 marks an empty cell).
// Output: puzzle, the completed table with values 1..N.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("N").get<int>();
  const auto& start = instance.at("start");

  // x[i][j][v] = 1 when cell (i, j) holds the value v + 1.
  std::vector<std::vector<std::vector<dcp::Lin>>> x(
      n, std::vector<std::vector<dcp::Lin>>(n, std::vector<dcp::Lin>(n)));
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j)
      for (int v = 0; v < n; ++v) {
        // a given cell fixes its value; an empty cell (0) leaves every value open
        int given = start[i][j].get<int>();
        double lo = (given == v + 1) ? 1 : 0;
        double hi = (given == 0 || given == v + 1) ? 1 : 0;
        x[i][j][v] = dcp::new_var(h, lo, hi);
      }

  // every cell holds exactly one value
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) {
      dcp::Lin one_value;
      for (int v = 0; v < n; ++v) one_value = one_value + x[i][j][v];
      dcp::add_row(h, one_value, 1, 1);
    }

  // every row contains each value exactly once
  for (int i = 0; i < n; ++i)
    for (int v = 0; v < n; ++v) {
      dcp::Lin in_row;
      for (int j = 0; j < n; ++j) in_row = in_row + x[i][j][v];
      dcp::add_row(h, in_row, 1, 1);
    }

  // every column contains each value exactly once
  for (int j = 0; j < n; ++j)
    for (int v = 0; v < n; ++v) {
      dcp::Lin in_column;
      for (int i = 0; i < n; ++i) in_column = in_column + x[i][j][v];
      dcp::add_row(h, in_column, 1, 1);
    }

  // the output cell p[i][j] is the value the cell holds, an integer from 1 to n
  std::vector<std::vector<dcp::Lin>> puzzle(n, std::vector<dcp::Lin>(n));
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) {
      dcp::Lin p = dcp::new_var(h, 1, n);
      dcp::Lin value = p;
      for (int v = 0; v < n; ++v) value = value - (double)(v + 1) * x[i][j][v];
      dcp::add_row(h, value, 0, 0);  // p = sum (v + 1) x[i][j][v]
      puzzle[i][j] = p;
    }

  out.add("puzzle", puzzle);
}
