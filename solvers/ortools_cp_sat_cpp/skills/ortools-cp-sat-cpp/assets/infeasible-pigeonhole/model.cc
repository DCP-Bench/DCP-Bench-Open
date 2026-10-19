// Place 4 pigeons into 3 holes so that no hole holds two pigeons.
// There is no such placement, and the solver must report INFEASIBLE.
#include <iostream>
#include <vector>

#include "ortools/sat/cp_model.h"
#include "ortools/sat/cp_model_solver.h"

using namespace operations_research;
using namespace operations_research::sat;

int main() {
  const int pigeons = 4;
  const int holes = 3;

  CpModelBuilder model;
  std::vector<IntVar> hole;
  std::vector<LinearExpr> hole_exprs;
  for (int p = 0; p < pigeons; ++p) {
    hole.push_back(model.NewIntVar(Domain(0, holes - 1)));
    hole_exprs.push_back(hole.back());
  }
  model.AddAllDifferent(hole_exprs);

  const CpSolverResponse response = Solve(model.Build());
  std::cout << "Status: " << CpSolverStatus_Name(response.status()) << "\n";
  if (response.status() == CpSolverStatus::INFEASIBLE) {
    std::cout << "No placement exists: the model is proven infeasible.\n";
  }
  return 0;
}
