// Discrete tomography: find a 0/1 matrix with the given number of ones in each row and each column.
// The matrix is output as a list of lists (one list per row), with 0 and 1 as values.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  std::vector<int> row_sums = instance.at("row_sums").get<std::vector<int>>();
  std::vector<int> col_sums = instance.at("col_sums").get<std::vector<int>>();
  int nr = row_sums.size();
  int nc = col_sums.size();

  // each cell is a binary column: 1 when the matrix holds a one there
  std::vector<std::vector<dcp::Lin>> cell(nr, std::vector<dcp::Lin>(nc));
  for (int i = 0; i < nr; ++i)
    for (int j = 0; j < nc; ++j)
      cell[i][j] = dcp::new_var(h, 0, 1);

  // the number of ones in each row equals the row sum
  for (int i = 0; i < nr; ++i) {
    dcp::Lin s = 0;
    for (int j = 0; j < nc; ++j) s = s + cell[i][j];
    dcp::add_row(h, s, row_sums[i], row_sums[i]);
  }

  // the number of ones in each column equals the column sum
  for (int j = 0; j < nc; ++j) {
    dcp::Lin s = 0;
    for (int i = 0; i < nr; ++i) s = s + cell[i][j];
    dcp::add_row(h, s, col_sums[j], col_sums[j]);
  }

  out.add("matrix", cell);
}
