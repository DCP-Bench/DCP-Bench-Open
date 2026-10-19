// Calvin puzzle: fill an n by n grid with the numbers 1 to n*n, each number once,
// so that every number is placed relative to the previous one either vertically or
// horizontally exactly three squares away, or diagonally exactly two squares away.
// Output x: the completed grid, x[i][j] is the number in row i, column j (0-based rows
// and columns, numbers 1-based).
#include "dcp.h"

#include <vector>

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n").get<int>();
  int N = n * n;
  using dcp::Lin;

  // P[k][i][j] = 1 when the number k+1 sits in row i, column j.
  std::vector<std::vector<std::vector<Lin>>> P(
      N, std::vector<std::vector<Lin>>(n, std::vector<Lin>(n)));
  for (int k = 0; k < N; ++k)
    for (int i = 0; i < n; ++i)
      for (int j = 0; j < n; ++j) P[k][i][j] = dcp::new_var(h, 0, 1);

  // every number is placed exactly once
  for (int k = 0; k < N; ++k) {
    Lin s;
    for (int i = 0; i < n; ++i)
      for (int j = 0; j < n; ++j) s = s + P[k][i][j];
    dcp::add_row(h, s, 1, 1);
  }

  // every square holds exactly one number
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) {
      Lin s;
      for (int k = 0; k < N; ++k) s = s + P[k][i][j];
      dcp::add_row(h, s, 1, 1);
    }

  // R[k] and C[k] are the row and the column of the number k+1
  std::vector<Lin> R(N), C(N);
  for (int k = 0; k < N; ++k) {
    R[k] = dcp::new_var(h, 0, n - 1);
    C[k] = dcp::new_var(h, 0, n - 1);
    Lin rowSum, colSum;
    for (int i = 0; i < n; ++i)
      for (int j = 0; j < n; ++j) {
        rowSum = rowSum + double(i) * P[k][i][j];
        colSum = colSum + double(j) * P[k][i][j];
      }
    dcp::add_row(h, rowSum - R[k], 0, 0);
    dcp::add_row(h, colSum - C[k], 0, 0);
  }

  // the eight allowed steps from one number to the next: vertical or horizontal
  // exactly three squares away (a two square gap), or diagonal exactly two squares
  // away (a one square gap)
  const int dRow[8] = {0, 0, 3, -3, 2, 2, -2, -2};
  const int dCol[8] = {3, -3, 0, 0, 2, -2, 2, -2};
  // the row and column differences lie within n - 1 and 3, so M = n + 2 bounds
  // every big-M row
  double M = n + 2;
  for (int k = 0; k + 1 < N; ++k) {
    // exactly one of the eight steps is chosen between number k+1 and number k+2
    std::vector<Lin> step(8);
    Lin pick;
    for (int o = 0; o < 8; ++o) {
      step[o] = dcp::new_var(h, 0, 1);
      pick = pick + step[o];
    }
    dcp::add_row(h, pick, 1, 1);

    // the row and column differences of the two numbers
    Lin dr = R[k + 1] - R[k];
    Lin dc = C[k + 1] - C[k];
    for (int o = 0; o < 8; ++o) {
      // if the step o is chosen, the row difference equals its row step
      dcp::add_row(h, (dr - double(dRow[o])) + M * step[o], -kHighsInf, M);
      dcp::add_row(h, (dr - double(dRow[o])) - M * step[o], -M, kHighsInf);
      // if the step o is chosen, the column difference equals its column step
      dcp::add_row(h, (dc - double(dCol[o])) + M * step[o], -kHighsInf, M);
      dcp::add_row(h, (dc - double(dCol[o])) - M * step[o], -M, kHighsInf);
    }
  }

  // the grid: x[i][j] is the number in row i, column j
  std::vector<std::vector<Lin>> x(n, std::vector<Lin>(n));
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) {
      Lin v;
      for (int k = 0; k < N; ++k) v = v + double(k + 1) * P[k][i][j];
      x[i][j] = v;
    }
  out.add("x", x);
}
