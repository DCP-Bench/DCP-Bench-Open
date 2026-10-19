// Coins on an n by n grid: place exactly c coins in each row and each column, with at most
// one coin per cell, minimising the sum of squared horizontal distances of the coins from the main diagonal.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n").get<int>();
  int c = instance.at("c").get<int>();

  // one binary per cell: 1 means a coin is placed there
  std::vector<std::vector<dcp::Lin>> x(n, std::vector<dcp::Lin>(n));
  for (int i = 0; i < n; i++)
    for (int j = 0; j < n; j++)
      x[i][j] = dcp::new_var(h, 0, 1, true);

  // exactly c coins in each row
  for (int i = 0; i < n; i++) {
    dcp::Lin row;
    for (int j = 0; j < n; j++) row = row + x[i][j];
    dcp::add_row(h, row, c, c);
  }

  // exactly c coins in each column
  for (int j = 0; j < n; j++) {
    dcp::Lin col;
    for (int i = 0; i < n; i++) col = col + x[i][j];
    dcp::add_row(h, col, c, c);
  }

  // the sum of the squared horizontal distance from the main diagonal over all coins
  // z is at most n*c coins, each at most (n-1)^2 away from the diagonal
  int maxz = n * c * (n - 1) * (n - 1);
  dcp::Lin z = dcp::new_var(h, 0, maxz, true);
  dcp::Lin dist;
  for (int i = 0; i < n; i++)
    for (int j = 0; j < n; j++)
      dist = dist + (i - j) * (i - j) * x[i][j];
  // z equals the total squared distance
  dcp::add_row(h, z - dist, 0, 0);

  out.minimize(z);
  out.add("z", z);
  out.add("x", x);
}
