#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Futoshiki: fill a square grid with the numbers 1..size so that each row and
// each column holds each number once, the given numbers are kept, and every
// "less than" sign between two neighbouring cells is respected.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  // values[row][col] is a given number, or 0 when the cell is empty.
  const std::vector<std::vector<int64_t>> values =
      instance.at("values").get<std::vector<std::vector<int64_t>>>();
  // Each entry [i1, j1, i2, j2] (1-based) says values[i1][j1] < values[i2][j2].
  const std::vector<std::vector<int>> lt =
      instance.at("lt").get<std::vector<std::vector<int>>>();
  const int size = static_cast<int>(values.size());

  // grid[row][col] is the number in that cell.
  std::vector<std::vector<IntVar>> grid(size);
  for (int row = 0; row < size; ++row)
    for (int col = 0; col < size; ++col) grid[row].push_back(model.NewIntVar(Domain(1, size)));

  // The numbers given at the start are kept.
  for (int row = 0; row < size; ++row)
    for (int col = 0; col < size; ++col)
      if (values[row][col] > 0) model.AddEquality(grid[row][col], values[row][col]);

  // Each row holds each number once.
  for (int row = 0; row < size; ++row) model.AddAllDifferent(grid[row]);

  // Each column holds each number once.
  for (int col = 0; col < size; ++col) {
    std::vector<IntVar> column;
    for (int row = 0; row < size; ++row) column.push_back(grid[row][col]);
    model.AddAllDifferent(column);
  }

  // Every inequality sign holds: the first cell is smaller than the second.
  for (const std::vector<int>& q : lt) {
    model.AddLessThan(grid[q[0] - 1][q[1] - 1], grid[q[2] - 1][q[3] - 1]);
  }

  json out = json::array();
  for (int row = 0; row < size; ++row) {
    json r = json::array();
    for (int col = 0; col < size; ++col) r.push_back(grid[row][col].index());
    out.push_back(r);
  }
  outputs = {{"grid", out}};
}
