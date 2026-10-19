// Complete a 4x4 Latin square: every row and every column holds 1..4 exactly once.
#include <iostream>
#include <vector>

#include "ortools/sat/cp_model.h"
#include "ortools/sat/cp_model_solver.h"

using namespace operations_research;
using namespace operations_research::sat;

int main() {
  // 0 marks an empty cell; any other number is a given clue.
  const std::vector<std::vector<int>> clues = {
      {1, 0, 0, 0},
      {0, 0, 0, 0},
      {4, 0, 2, 0},
      {0, 4, 1, 3}};
  const int n = static_cast<int>(clues.size());

  CpModelBuilder model;
  std::vector<std::vector<IntVar>> cell(n);
  for (int r = 0; r < n; ++r) {
    for (int c = 0; c < n; ++c) {
      cell[r].push_back(model.NewIntVar(Domain(1, n)));
    }
  }

  for (int r = 0; r < n; ++r) {
    // AddAllDifferent takes LinearExpr, so convert the IntVars first.
    std::vector<LinearExpr> row(cell[r].begin(), cell[r].end());
    model.AddAllDifferent(row);
    std::vector<LinearExpr> column;
    for (int k = 0; k < n; ++k) column.push_back(cell[k][r]);
    model.AddAllDifferent(column);
  }

  for (int r = 0; r < n; ++r) {
    for (int c = 0; c < n; ++c) {
      if (clues[r][c] != 0) model.AddEquality(cell[r][c], clues[r][c]);
    }
  }

  const CpSolverResponse response = Solve(model.Build());
  std::cout << "Status: " << CpSolverStatus_Name(response.status()) << "\n";
  if (response.status() != CpSolverStatus::OPTIMAL &&
      response.status() != CpSolverStatus::FEASIBLE) {
    return 0;
  }
  for (int r = 0; r < n; ++r) {
    for (int c = 0; c < n; ++c) {
      std::cout << SolutionIntegerValue(response, cell[r][c])
                << (c + 1 < n ? " " : "\n");
    }
  }
  return 0;
}
