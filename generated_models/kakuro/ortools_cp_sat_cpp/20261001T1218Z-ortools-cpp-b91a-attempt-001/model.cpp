#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Kakuro: put a digit from 1 to 9 into each white cell of an n x n grid so
// that the digits of every entry (a run of cells) add up to the clue for that
// entry and no digit repeats inside an entry. Blank (black) cells hold 0.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();
  // blanks[i] = [row, col], 1-based: the cells that are not white.
  const std::vector<std::vector<int>> blanks =
      instance.at("blanks").get<std::vector<std::vector<int>>>();
  // problem[p] = [sum, [row, col], [row, col], ...]: the entry's clue followed
  // by its cells (1-based). Entries differ in length, so it is read as JSON.
  const json& problem = instance.at("problem");

  // x[i][j] is the digit in row i, column j; 0 is the value of a blank cell.
  std::vector<std::vector<IntVar>> x(n);
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) x[i].push_back(model.NewIntVar(Domain(0, 9)));

  // Blank cells are filled with 0.
  for (const std::vector<int>& cell : blanks) model.AddEquality(x[cell[0] - 1][cell[1] - 1], 0);

  for (const json& entry : problem) {
    const int64_t clue = entry.at(0).get<int64_t>();
    std::vector<IntVar> segment;
    LinearExpr segment_sum;
    for (size_t k = 1; k < entry.size(); ++k) {
      const IntVar cell = x[entry.at(k).at(0).get<int>() - 1][entry.at(k).at(1).get<int>() - 1];
      // Every cell of an entry holds a positive digit.
      model.AddGreaterOrEqual(cell, 1);
      segment.push_back(cell);
      segment_sum += cell;
    }
    // The digits of the entry add up to its clue.
    model.AddEquality(segment_sum, clue);
    // No digit repeats inside an entry.
    model.AddAllDifferent(segment);
  }

  json out = json::array();
  for (int i = 0; i < n; ++i) {
    json row = json::array();
    for (int j = 0; j < n; ++j) row.push_back(x[i][j].index());
    out.push_back(row);
  }
  outputs = {{"x", out}};
}
