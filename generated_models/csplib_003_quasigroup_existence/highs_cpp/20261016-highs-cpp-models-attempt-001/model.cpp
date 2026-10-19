// CSPLib 003, quasigroup existence (QG3.m): an order m quasigroup is a Latin square of size m
// (each element occurs once in every row and column), and (a*b)*(b*a) = a for all a, b.
// The output quasigroup is an m x m table of integers 0..m-1.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int m = instance.at("m").get<int>();

  // y[i][j][v] = 1 when the table entry at row i, column j is the value v.
  std::vector<std::vector<std::vector<dcp::Lin>>> y(m, std::vector<std::vector<dcp::Lin>>(m));
  for (int i = 0; i < m; ++i)
    for (int j = 0; j < m; ++j)
      for (int v = 0; v < m; ++v) y[i][j].push_back(dcp::new_var(h, 0, 1));

  // every cell holds exactly one value
  for (int i = 0; i < m; ++i)
    for (int j = 0; j < m; ++j) {
      dcp::Lin one_value;
      for (int v = 0; v < m; ++v) one_value = one_value + y[i][j][v];
      dcp::add_row(h, one_value, 1, 1);
    }

  // every row contains each element once
  for (int i = 0; i < m; ++i)
    for (int v = 0; v < m; ++v) {
      dcp::Lin in_row;
      for (int j = 0; j < m; ++j) in_row = in_row + y[i][j][v];
      dcp::add_row(h, in_row, 1, 1);
    }

  // every column contains each element once
  for (int j = 0; j < m; ++j)
    for (int v = 0; v < m; ++v) {
      dcp::Lin in_column;
      for (int i = 0; i < m; ++i) in_column = in_column + y[i][j][v];
      dcp::add_row(h, in_column, 1, 1);
    }

  // (a*b)*(b*a) = a: if the entry a*b is k and the entry b*a is l, then the entry k*l is a
  // (a clause on the one-hot binaries: not (a*b = k) or not (b*a = l) or (k*l = a))
  for (int a = 0; a < m; ++a)
    for (int b = 0; b < m; ++b)
      for (int k = 0; k < m; ++k)
        for (int l = 0; l < m; ++l)
          dcp::add_row(h, y[a][b][k] + y[b][a][l] - y[k][l][a], -kHighsInf, 1);

  // the table entry at row i, column j is the sum of v times its indicator
  std::vector<std::vector<dcp::Lin>> quasigroup(m, std::vector<dcp::Lin>(m));
  for (int i = 0; i < m; ++i)
    for (int j = 0; j < m; ++j)
      for (int v = 0; v < m; ++v) quasigroup[i][j] = quasigroup[i][j] + v * y[i][j][v];

  out.add("quasigroup", quasigroup);
}
