#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Coins grid: place coins on an n by n grid, at most one per cell and exactly c
// in every row and every column, so that the sum of the squared horizontal
// distances of the coins from the main diagonal is as small as possible.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();  // grid size
  const int c = instance.at("c").get<int>();  // coins per row and column

  // x[i][j] is 1 when a coin is placed in cell (i, j), else 0.  Each cell
  // holds at most one coin, which the 0..1 domain states.
  std::vector<std::vector<IntVar>> x(n);
  for (int i = 0; i < n; ++i) {
    for (int j = 0; j < n; ++j) x[i].push_back(model.NewIntVar(Domain(0, 1)));
  }

  // Every row holds exactly c coins.
  for (int i = 0; i < n; ++i) {
    LinearExpr coins_in_row;
    for (int j = 0; j < n; ++j) coins_in_row += x[i][j];
    model.AddEquality(coins_in_row, c);
  }
  // Every column holds exactly c coins.
  for (int j = 0; j < n; ++j) {
    LinearExpr coins_in_column;
    for (int i = 0; i < n; ++i) coins_in_column += x[i][j];
    model.AddEquality(coins_in_column, c);
  }

  // z: the sum over all coins of the squared horizontal distance |i - j| from
  // the main diagonal.  Its upper bound is the sum with a coin in every cell.
  LinearExpr distance_sum;
  int64_t distance_bound = 0;
  for (int i = 0; i < n; ++i) {
    for (int j = 0; j < n; ++j) {
      const int64_t d = (i > j) ? (i - j) : (j - i);
      distance_sum += (d * d) * x[i][j];
      distance_bound += d * d;
    }
  }
  IntVar z = model.NewIntVar(Domain(0, distance_bound));
  model.AddEquality(z, distance_sum);

  // Keep the coins as close to the main diagonal as possible.
  model.Minimize(z);

  json x_out = json::array();
  for (int i = 0; i < n; ++i) {
    json row = json::array();
    for (int j = 0; j < n; ++j) row.push_back(x[i][j].index());
    x_out.push_back(row);
  }
  outputs = {{"x", x_out}, {"z", z.index()}};
}
