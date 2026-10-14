#include <algorithm>
#include <cstdlib>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Flip rows and columns: given a matrix of positive and negative numbers,
// choose a sign (+1 or -1) for every row and every column, flipping the signs
// of the entries, so that every row sum and every column sum is >= 0, and the
// total sum of the flipped matrix is as small as possible.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<std::vector<int64_t>> input_matrix =
      instance.at("input_matrix").get<std::vector<std::vector<int64_t>>>();
  const int rows = static_cast<int>(input_matrix.size());
  const int cols = static_cast<int>(input_matrix[0].size());

  // Bounds derived from the data: no flipped entry exceeds the largest
  // absolute entry, and no sum exceeds the sum of the absolute entries it covers.
  int64_t max_abs = 0, total_abs = 0;
  std::vector<int64_t> row_abs(rows, 0), col_abs(cols, 0);
  for (int i = 0; i < rows; ++i) {
    for (int j = 0; j < cols; ++j) {
      const int64_t v = std::llabs(input_matrix[i][j]);
      max_abs = std::max(max_abs, v);
      row_abs[i] += v;
      col_abs[j] += v;
      total_abs += v;
    }
  }

  // row_signs[i] and col_signs[j] are -1 (flip) or +1 (keep); 0 is not allowed.
  std::vector<IntVar> row_signs, col_signs;
  for (int i = 0; i < rows; ++i) row_signs.push_back(model.NewIntVar(Domain::FromValues({-1, 1})));
  for (int j = 0; j < cols; ++j) col_signs.push_back(model.NewIntVar(Domain::FromValues({-1, 1})));

  // x[i][j] is the entry after flipping: input * row sign * column sign.
  // The two signs are multiplied first (a product of two variables), then
  // scaled by the constant entry.
  std::vector<std::vector<IntVar>> x(rows);
  for (int i = 0; i < rows; ++i) {
    for (int j = 0; j < cols; ++j) {
      const IntVar sign = model.NewIntVar(Domain::FromValues({-1, 1}));
      model.AddMultiplicationEquality(sign, {row_signs[i], col_signs[j]});
      const IntVar entry = model.NewIntVar(Domain(-max_abs, max_abs));
      model.AddEquality(entry, input_matrix[i][j] * sign);
      x[i].push_back(entry);
    }
  }

  // Every row of the flipped matrix sums to a non-negative number.
  for (int i = 0; i < rows; ++i) {
    LinearExpr row_sum;
    for (int j = 0; j < cols; ++j) row_sum += x[i][j];
    const IntVar row_sums = model.NewIntVar(Domain(0, row_abs[i]));
    model.AddEquality(row_sums, row_sum);
  }

  // Every column of the flipped matrix sums to a non-negative number.
  for (int j = 0; j < cols; ++j) {
    LinearExpr col_sum;
    for (int i = 0; i < rows; ++i) col_sum += x[i][j];
    const IntVar col_sums = model.NewIntVar(Domain(0, col_abs[j]));
    model.AddEquality(col_sums, col_sum);
  }

  // total_sum is the sum of all entries of the flipped matrix, to be minimized.
  LinearExpr all_entries;
  for (int i = 0; i < rows; ++i)
    for (int j = 0; j < cols; ++j) all_entries += x[i][j];
  const IntVar total_sum = model.NewIntVar(Domain(0, total_abs));
  model.AddEquality(total_sum, all_entries);
  model.Minimize(total_sum);

  json row_out = json::array(), col_out = json::array();
  for (const IntVar& v : row_signs) row_out.push_back(v.index());
  for (const IntVar& v : col_signs) col_out.push_back(v.index());
  outputs = {{"row_signs", row_out}, {"col_signs", col_out}};
}
