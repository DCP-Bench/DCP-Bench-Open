// Plan integer quantities of two products to maximise profit under two limits:
//   2x + y <= 14 hours of machine time,   x + 2y <= 14 hours of assembly.
#include <cstdint>
#include <iostream>

#include "ortools/sat/cp_model.h"
#include "ortools/sat/cp_model_solver.h"

using namespace operations_research;
using namespace operations_research::sat;

int main() {
  CpModelBuilder model;
  const IntVar chairs = model.NewIntVar(Domain(0, 100));
  const IntVar tables = model.NewIntVar(Domain(0, 100));

  model.AddLessOrEqual(2 * chairs + tables, 14);
  model.AddLessOrEqual(chairs + 2 * tables, 14);

  // Profit per unit is 40 for a chair and 50 for a table. The objective must
  // be an integer linear expression.
  model.Maximize(40 * chairs + 50 * tables);

  const CpSolverResponse response = Solve(model.Build());
  std::cout << "Status: " << CpSolverStatus_Name(response.status()) << "\n";
  if (response.status() != CpSolverStatus::OPTIMAL) return 0;
  std::cout << "Maximum profit: " << static_cast<int64_t>(response.objective_value()) << "\n";
  std::cout << "chairs = " << SolutionIntegerValue(response, chairs) << "\n";
  std::cout << "tables = " << SolutionIntegerValue(response, tables) << "\n";
  return 0;
}
