// Flip the sign of whole rows and whole columns of an integer array so that every row and
// every column sums to a positive number (or zero), and the overall sum is as small as possible.
// Outputs: row_signs and col_signs, each entry -1 (flipped) or 1 (kept).
//
// Formulation: b[i] = 1 when row i is kept (sign +1), z[j] = 1 when column j is flipped.
// S[i] is the row sum after the column flips only. A row is non-negative after its own flip
// exactly when its sign follows the sign of S[i], so the row total is |S[i]|. The objective
// is the sum of |S[i]|, linearised with u[i] >= S[i] and u[i] >= -S[i].
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  std::vector<std::vector<int>> a = instance.at("input_matrix").get<std::vector<std::vector<int>>>();
  const int R = static_cast<int>(a.size());
  const int C = static_cast<int>(a[0].size());

  // Big-M constants from the data: the largest magnitude of each row and column sum.
  std::vector<double> row_big(R, 0), col_big(C, 0);
  for (int i = 0; i < R; ++i)
    for (int j = 0; j < C; ++j) {
      row_big[i] += std::abs(a[i][j]);
      col_big[j] += std::abs(a[i][j]);
    }

  std::vector<dcp::Lin> b, z, u;
  for (int i = 0; i < R; ++i) b.push_back(dcp::new_var(h, 0, 1));
  for (int j = 0; j < C; ++j) z.push_back(dcp::new_var(h, 0, 1));
  for (int i = 0; i < R; ++i) u.push_back(dcp::new_var(h, 0, kHighsInf, false));

  // the row sum after the column flips: S[i] = sum_j a[i][j] (1 - 2 z[j])
  std::vector<dcp::Lin> S(R);
  for (int i = 0; i < R; ++i) {
    dcp::Lin s(0);
    for (int j = 0; j < C; ++j) s = s + (static_cast<double>(a[i][j]) - 2.0 * a[i][j] * z[j]);
    S[i] = s;
  }

  // the objective is the sum of the absolute row sums: u[i] >= S[i] and u[i] >= -S[i]
  for (int i = 0; i < R; ++i) {
    dcp::add_row(h, u[i] - S[i], 0, kHighsInf);
    dcp::add_row(h, u[i] + S[i], 0, kHighsInf);
  }

  // every row sums to a positive number or zero: the row sign b[i] follows the sign of S[i]
  // when b[i] = 1 then S[i] >= 0, and when b[i] = 0 then S[i] <= 0
  for (int i = 0; i < R; ++i) {
    double M = row_big[i];
    dcp::add_row(h, S[i] - M * b[i], -M, kHighsInf);
    dcp::add_row(h, S[i] - M * b[i], -kHighsInf, 0);
  }

  // every column sums to a positive number or zero: the signed column sum C[j] has the sign of
  // the column flip. The column is kept (z[j] = 0) then C[j] >= 0, and flipped then C[j] <= 0.
  // C[j] = sum_i a[i][j] (2 b[i] - 1)
  for (int j = 0; j < C; ++j) {
    double N = col_big[j];
    dcp::Lin c(0);
    for (int i = 0; i < R; ++i) c = c + (2.0 * a[i][j] * b[i] - static_cast<double>(a[i][j]));
    dcp::add_row(h, c + N * z[j], 0, kHighsInf);
    dcp::add_row(h, c + N * z[j], -kHighsInf, N);
  }

  // the overall sum of the array is minimised
  dcp::Lin total(0);
  for (int i = 0; i < R; ++i) total = total + u[i];
  out.minimize(total);

  // signs: -1 for a flipped row or column, 1 otherwise
  std::vector<dcp::Lin> row_signs, col_signs;
  for (int i = 0; i < R; ++i) row_signs.push_back(dcp::Lin(-1.0) + 2.0 * b[i]);
  for (int j = 0; j < C; ++j) col_signs.push_back(dcp::Lin(1.0) + (-2.0) * z[j]);
  out.add("row_signs", row_signs);
  out.add("col_signs", col_signs);
}
