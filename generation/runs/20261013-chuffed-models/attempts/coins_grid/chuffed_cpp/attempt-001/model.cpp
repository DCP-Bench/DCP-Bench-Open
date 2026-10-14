// Coins grid: place coins on an n x n board so that every row and every column holds
// exactly c coins, at most one coin per cell, minimizing the sum of squared horizontal
// distances of the coins from the main diagonal.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");
  int c = instance.at("c");

  // coin[i][j] = 1 if a coin is placed in row i, column j (at most one per cell by domain)
  vec<vec<IntVar*>> coin;
  createVars(coin, n, n, 0, 1, true);

  // every row holds exactly c coins
  for (int i = 0; i < n; ++i) {
    vec<IntVar*> row;
    for (int j = 0; j < n; ++j) row.push(coin[i][j]);
    int_linear(row, IRT_EQ, c);
  }

  // every column holds exactly c coins
  for (int j = 0; j < n; ++j) {
    vec<IntVar*> col;
    for (int i = 0; i < n; ++i) col.push(coin[i][j]);
    int_linear(col, IRT_EQ, c);
  }

  // the cost is the sum over the coins of the squared horizontal distance (j - i)^2 from the main diagonal
  vec<IntVar*> cells;
  vec<int> dist2;
  for (int i = 0; i < n; ++i) {
    for (int j = 0; j < n; ++j) {
      cells.push(coin[i][j]);
      dist2.push((j - i) * (j - i));
    }
  }
  int max_cost = n * c * (n - 1) * (n - 1);
  IntVar* z = newIntVar(0, max_cost);
  int_linear(dist2, cells, IRT_EQ, z);

  // branch on the coin cells in row order
  branch(cells, VAR_INORDER, VAL_MIN);
  optimize(z, OPT_MIN);

  json x = json::array();
  for (int i = 0; i < n; ++i) {
    json row = json::array();
    for (int j = 0; j < n; ++j) row.push_back(dcp::out(coin[i][j]));
    x.push_back(row);
  }
  outputs = {{"x", x}, {"z", dcp::out(z)}};
}
