// Discrete tomography: find a 0/1 matrix whose row sums and column sums are the given X-ray counts.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<int> row_sums = instance.at("row_sums").get<std::vector<int>>();
  std::vector<int> col_sums = instance.at("col_sums").get<std::vector<int>>();
  int R = static_cast<int>(row_sums.size());
  int C = static_cast<int>(col_sums.size());

  // cell[i][j] = 1 if the matrix has a one in row i, column j
  vec<vec<IntVar*>> cell;
  createVars(cell, R, C, 0, 1, true);

  // every row contains as many ones as its row sum says
  for (int i = 0; i < R; ++i) {
    // the ones in row i
    vec<IntVar*> row;
    for (int j = 0; j < C; ++j) row.push(cell[i][j]);
    int_linear(row, IRT_EQ, row_sums[i]);
  }

  // every column contains as many ones as its column sum says
  for (int j = 0; j < C; ++j) {
    // the ones in column j
    vec<IntVar*> col;
    for (int i = 0; i < R; ++i) col.push(cell[i][j]);
    int_linear(col, IRT_EQ, col_sums[j]);
  }

  // branch on the cells row by row
  vec<IntVar*> flat;
  flatten(cell, flat);
  branch(flat, VAR_INORDER, VAL_MIN);

  json matrix = json::array();
  for (int i = 0; i < R; ++i) {
    json r = json::array();
    for (int j = 0; j < C; ++j) r.push_back(dcp::out(cell[i][j]));
    matrix.push_back(r);
  }
  outputs = {{"matrix", matrix}};
}
