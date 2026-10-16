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

  // P[k][c] = 1 when the number k+1 sits on square c, where square c = (i, j) is
  // index i * n + j.
  std::vector<std::vector<Lin>> P(N, std::vector<Lin>(N));
  for (int k = 0; k < N; ++k)
    for (int c = 0; c < N; ++c) P[k][c] = dcp::new_var(h, 0, 1);

  // every number is placed exactly once
  for (int k = 0; k < N; ++k) {
    Lin s;
    for (int c = 0; c < N; ++c) s = s + P[k][c];
    dcp::add_row(h, s, 1, 1);
  }

  // every square holds exactly one number
  for (int c = 0; c < N; ++c) {
    Lin s;
    for (int k = 0; k < N; ++k) s = s + P[k][c];
    dcp::add_row(h, s, 1, 1);
  }

  // the eight steps: vertical or horizontal exactly three squares away (a two square
  // gap), or diagonal exactly two squares away (a one square gap)
  const int dRow[8] = {0, 0, 3, -3, 2, 2, -2, -2};
  const int dCol[8] = {3, -3, 0, 0, 2, -2, 2, -2};

  // the squares reachable from square c in one step
  auto reachable = [&](int c) {
    int i = c / n, j = c % n;
    std::vector<int> to;
    for (int o = 0; o < 8; ++o) {
      int a = i + dRow[o], b = j + dCol[o];
      if (a >= 0 && a < n && b >= 0 && b < n) to.push_back(a * n + b);
    }
    return to;
  };

  // if the number k+1 sits on square c, then the number k+2 sits on a square reachable
  // from c in one step. Written as: the squares reachable from c hold k+2 at least
  // as often as c holds k+1 (both sides are one-hot, so this is exact).
  for (int k = 0; k + 1 < N; ++k)
    for (int c = 0; c < N; ++c) {
      Lin s;
      for (int d : reachable(c)) s = s + P[k + 1][d];
      dcp::add_row(h, s - P[k][c], 0, kHighsInf);
    }

  // the same from the other side: if the number k+2 sits on square d, then the number
  // k+1 sits on a square from which d is reachable in one step (steps are symmetric)
  for (int k = 0; k + 1 < N; ++k)
    for (int d = 0; d < N; ++d) {
      Lin s;
      for (int c : reachable(d)) s = s + P[k][c];
      dcp::add_row(h, s - P[k + 1][d], 0, kHighsInf);
    }

  // the grid: x[i][j] is the number in row i, column j
  std::vector<std::vector<Lin>> x(n, std::vector<Lin>(n));
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) {
      Lin v;
      for (int k = 0; k < N; ++k) v = v + double(k + 1) * P[k][i * n + j];
      x[i][j] = v;
    }
  out.add("x", x);
}
