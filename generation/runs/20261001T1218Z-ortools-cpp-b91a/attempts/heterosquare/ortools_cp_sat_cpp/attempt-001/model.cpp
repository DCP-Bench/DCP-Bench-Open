#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Heterosquare: fill an n x n square with distinct integers from 1 to n^2 so
// that the sums of the n rows, the n columns and the two diagonals are all
// different from each other.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();
  // A line sum is at most n entries of at most n^2 each, i.e. n^3.
  const int64_t max_sum = static_cast<int64_t>(n) * n * n;

  // x[i][j] is the entry in row i, column j.
  std::vector<std::vector<IntVar>> x(n);
  std::vector<IntVar> all_entries;
  for (int i = 0; i < n; ++i) {
    for (int j = 0; j < n; ++j) {
      x[i].push_back(model.NewIntVar(Domain(1, static_cast<int64_t>(n) * n)));
      all_entries.push_back(x[i][j]);
    }
  }

  // All the entries in the square are different.
  model.AddAllDifferent(all_entries);

  // Sums of the rows, the columns and the two diagonals.
  std::vector<IntVar> row_sums, col_sums;
  for (int i = 0; i < n; ++i) row_sums.push_back(model.NewIntVar(Domain(1, max_sum)));
  for (int j = 0; j < n; ++j) col_sums.push_back(model.NewIntVar(Domain(1, max_sum)));
  const IntVar diag1 = model.NewIntVar(Domain(1, max_sum));
  const IntVar diag2 = model.NewIntVar(Domain(1, max_sum));

  // Row sums.
  for (int i = 0; i < n; ++i) {
    LinearExpr s;
    for (int j = 0; j < n; ++j) s += x[i][j];
    model.AddEquality(row_sums[i], s);
  }
  // Column sums.
  for (int j = 0; j < n; ++j) {
    LinearExpr s;
    for (int i = 0; i < n; ++i) s += x[i][j];
    model.AddEquality(col_sums[j], s);
  }
  // Main diagonal (top-left to bottom-right) and anti-diagonal.
  LinearExpr d1, d2;
  for (int i = 0; i < n; ++i) {
    d1 += x[i][i];
    d2 += x[i][n - i - 1];
  }
  model.AddEquality(diag1, d1);
  model.AddEquality(diag2, d2);

  // All 2n + 2 sums are different from each other.
  std::vector<IntVar> all_sums;
  all_sums.insert(all_sums.end(), row_sums.begin(), row_sums.end());
  all_sums.insert(all_sums.end(), col_sums.begin(), col_sums.end());
  all_sums.push_back(diag1);
  all_sums.push_back(diag2);
  model.AddAllDifferent(all_sums);

  json out = json::array();
  for (int i = 0; i < n; ++i) {
    json row = json::array();
    for (int j = 0; j < n; ++j) row.push_back(x[i][j].index());
    out.push_back(row);
  }
  outputs = {{"x", out}};
}
