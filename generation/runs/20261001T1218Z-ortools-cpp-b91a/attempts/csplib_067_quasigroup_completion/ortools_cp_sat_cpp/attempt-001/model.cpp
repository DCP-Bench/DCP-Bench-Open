#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Quasigroup completion: complete a partially filled N x N Latin square, so
// that each number from 1 to N occurs exactly once in every row and column.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int N = instance.at("N").get<int>();
  // start[i][j] is the given number, or 0 when the cell is empty.
  const std::vector<std::vector<int64_t>> start =
      instance.at("start").get<std::vector<std::vector<int64_t>>>();

  // puzzle[i][j] is the number in row i, column j.
  std::vector<std::vector<IntVar>> puzzle(N);
  for (int i = 0; i < N; ++i) {
    for (int j = 0; j < N; ++j) puzzle[i].push_back(model.NewIntVar(Domain(1, N)));
  }

  // The cells that are already filled in keep their given number.
  for (int i = 0; i < N; ++i) {
    for (int j = 0; j < N; ++j) {
      if (start[i][j] != 0) model.AddEquality(puzzle[i][j], start[i][j]);
    }
  }

  // Each row holds each number once.
  for (int i = 0; i < N; ++i) model.AddAllDifferent(puzzle[i]);

  // Each column holds each number once.
  for (int j = 0; j < N; ++j) {
    std::vector<IntVar> column;
    for (int i = 0; i < N; ++i) column.push_back(puzzle[i][j]);
    model.AddAllDifferent(column);
  }

  json out = json::array();
  for (int i = 0; i < N; ++i) {
    json row = json::array();
    for (int j = 0; j < N; ++j) row.push_back(puzzle[i][j].index());
    out.push_back(row);
  }
  outputs = {{"puzzle", out}};
}
