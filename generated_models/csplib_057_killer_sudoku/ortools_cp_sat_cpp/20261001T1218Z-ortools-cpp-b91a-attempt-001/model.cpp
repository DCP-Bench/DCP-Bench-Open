#include <cmath>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Killer sudoku: fill an n x n grid with 1..n so that every row, column and
// box holds each number once, and every cage (a group of cells with a printed
// sum) adds up to its sum with no number repeated inside the cage.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();
  // The boxes are b x b blocks with b * b == n (3 x 3 for the usual 9 x 9 grid).
  const int b = static_cast<int>(std::lround(std::sqrt(static_cast<double>(n))));

  // x[r][c] is the number written in row r, column c.
  std::vector<std::vector<IntVar>> x(n);
  for (int r = 0; r < n; ++r) {
    for (int c = 0; c < n; ++c) x[r].push_back(model.NewIntVar(Domain(1, n)));
  }

  // All rows must hold distinct numbers.
  for (int r = 0; r < n; ++r) model.AddAllDifferent(x[r]);

  // All columns must hold distinct numbers.
  for (int c = 0; c < n; ++c) {
    std::vector<IntVar> column;
    for (int r = 0; r < n; ++r) column.push_back(x[r][c]);
    model.AddAllDifferent(column);
  }

  // Each b x b box must hold distinct numbers.
  for (int i = 0; i < b; ++i) {
    for (int j = 0; j < b; ++j) {
      std::vector<IntVar> box;
      for (int r = i * b; r < i * b + b; ++r) {
        for (int c = j * b; c < j * b + b; ++c) box.push_back(x[r][c]);
      }
      model.AddAllDifferent(box);
    }
  }

  // Cages: each entry is [sum, [[row, col], ...]] with 1-based cells.
  // The numbers in a cage add up to its sum and are all different.
  for (const json& cage_spec : instance.at("problem")) {
    const int64_t target_sum = cage_spec.at(0).get<int64_t>();
    std::vector<IntVar> cage;
    LinearExpr cage_total;
    for (const json& cell : cage_spec.at(1)) {
      const IntVar v = x[cell.at(0).get<int>() - 1][cell.at(1).get<int>() - 1];
      cage.push_back(v);
      cage_total += v;
    }
    model.AddEquality(cage_total, target_sum);
    model.AddAllDifferent(cage);
  }

  json out = json::array();
  for (int r = 0; r < n; ++r) {
    json row = json::array();
    for (int c = 0; c < n; ++c) row.push_back(x[r][c].index());
    out.push_back(row);
  }
  outputs = {{"x", out}};
}
