// Flip rows and columns: choose the sign of each row and column so that every row and every
// column of the matrix sums to a non-negative number, and the total of the matrix is minimal.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<std::vector<int>> input = instance.at("input_matrix").get<std::vector<std::vector<int>>>();
  int rows = static_cast<int>(input.size());
  int cols = static_cast<int>(input[0].size());

  // row_sign[i] and col_sign[j] are the chosen signs, each -1 or 1
  vec<IntVar*> row_sign;
  createVars(row_sign, rows, -1, 1);
  vec<IntVar*> col_sign;
  createVars(col_sign, cols, -1, 1);
  // a sign is never zero
  for (int i = 0; i < rows; ++i) int_rel(row_sign[i], IRT_NE, 0);
  for (int j = 0; j < cols; ++j) int_rel(col_sign[j], IRT_NE, 0);

  // flipped[i][j] = row_sign[i] * col_sign[j] is the sign applied to the entry in row i, column j
  vec<vec<IntVar*>> flipped;
  createVars(flipped, rows, cols, -1, 1);
  for (int i = 0; i < rows; ++i) {
    for (int j = 0; j < cols; ++j) {
      // the entry is flipped by its row and by its column
      int_times(row_sign[i], col_sign[j], flipped[i][j]);
    }
  }

  // every row of the flipped matrix sums to a non-negative number
  for (int i = 0; i < rows; ++i) {
    // the row sum after flipping is the sum of the input entries times their flips
    vec<int> coef;
    vec<IntVar*> sign;
    for (int j = 0; j < cols; ++j) {
      coef.push(input[i][j]);
      sign.push(flipped[i][j]);
    }
    int_linear(coef, sign, IRT_GE, 0);
  }

  // every column of the flipped matrix sums to a non-negative number
  for (int j = 0; j < cols; ++j) {
    // the column sum after flipping is the sum of the input entries times their flips
    vec<int> coef;
    vec<IntVar*> sign;
    for (int i = 0; i < rows; ++i) {
      coef.push(input[i][j]);
      sign.push(flipped[i][j]);
    }
    int_linear(coef, sign, IRT_GE, 0);
  }

  // total is the sum of all entries of the flipped matrix, to be minimized
  int bound = 0;
  for (const auto& row : input) {
    for (int v : row) bound += v < 0 ? -v : v;
  }
  IntVar* total = newIntVar(-bound, bound);
  vec<int> all_coef;
  vec<IntVar*> all_sign;
  for (int i = 0; i < rows; ++i) {
    for (int j = 0; j < cols; ++j) {
      all_coef.push(input[i][j]);
      all_sign.push(flipped[i][j]);
    }
  }
  int_linear(all_coef, all_sign, IRT_EQ, total);

  // search over the row signs, then the column signs
  vec<IntVar*> signs;
  for (int i = 0; i < rows; ++i) signs.push(row_sign[i]);
  for (int j = 0; j < cols; ++j) signs.push(col_sign[j]);
  branch(signs, VAR_INORDER, VAL_MIN);
  optimize(total, OPT_MIN);

  json rows_out = json::array();
  for (int i = 0; i < rows; ++i) rows_out.push_back(dcp::out(row_sign[i]));
  json cols_out = json::array();
  for (int j = 0; j < cols; ++j) cols_out.push_back(dcp::out(col_sign[j]));
  outputs = {{"row_signs", rows_out}, {"col_signs", cols_out}};
}
