// Coins grid: place coins on an n x n board so that every row and every column holds
// exactly c coins, at most one coin per cell, minimizing the sum of squared horizontal
// distances of the coins from the main diagonal.
#include "dcp.h"

#include <algorithm>
#include <vector>

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

  // cost of row i: the squared distance (j - i)^2 of each coin in that row from the diagonal.
  // Since the row holds exactly c coins, its cost lies between the sum of the c smallest and
  // the sum of the c largest squared distances in that row; these bounds are given to the
  // solver explicitly so that the total cost starts with a useful lower bound.
  vec<IntVar*> row_cost;
  int total_lo = 0, total_hi = 0;
  for (int i = 0; i < n; ++i) {
    std::vector<int> d;
    for (int j = 0; j < n; ++j) d.push_back((j - i) * (j - i));
    std::sort(d.begin(), d.end());
    int lo = 0, hi = 0;
    for (int k = 0; k < c; ++k) {
      lo += d[k];
      hi += d[n - 1 - k];
    }
    total_lo += lo;
    total_hi += hi;

    // cost of row i = sum over its cells of squared distance times coin
    vec<IntVar*> cells;
    vec<int> dist2;
    for (int j = 0; j < n; ++j) {
      cells.push(coin[i][j]);
      dist2.push((j - i) * (j - i));
    }
    IntVar* rc = newIntVar(lo, hi);
    int_linear(dist2, cells, IRT_EQ, rc);
    row_cost.push(rc);
  }

  // the cost z is the sum of the row costs
  IntVar* z = newIntVar(total_lo, total_hi);
  vec<int> ones;
  for (int i = 0; i < n; ++i) ones.push(1);
  int_linear(ones, row_cost, IRT_EQ, z);

  // branch on the cells nearest the diagonal first, and try a coin there first
  std::vector<int> order(n * n);
  for (int k = 0; k < n * n; ++k) order[k] = k;
  std::stable_sort(order.begin(), order.end(), [&](int a, int b) {
    int da = (a % n - a / n) * (a % n - a / n);
    int db = (b % n - b / n) * (b % n - b / n);
    return da < db;
  });
  vec<IntVar*> search;
  for (int k : order) search.push(coin[k / n][k % n]);
  branch(search, VAR_INORDER, VAL_MAX);
  optimize(z, OPT_MIN);

  json x = json::array();
  for (int i = 0; i < n; ++i) {
    json row = json::array();
    for (int j = 0; j < n; ++j) row.push_back(dcp::out(coin[i][j]));
    x.push_back(row);
  }
  outputs = {{"x", x}, {"z", dcp::out(z)}};
}
