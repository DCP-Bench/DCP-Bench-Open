// Assign each of 4 workers to a different task at the lowest total cost.
#include <cstdint>
#include <iostream>
#include <vector>

#include "ortools/sat/cp_model.h"
#include "ortools/sat/cp_model_solver.h"

using namespace operations_research;
using namespace operations_research::sat;

int main() {
  // cost[w][t]: cost of worker w doing task t.
  const std::vector<std::vector<int64_t>> cost = {
      {9, 2, 7, 8},
      {6, 4, 3, 7},
      {5, 8, 1, 8},
      {7, 6, 9, 4}};
  const int n = static_cast<int>(cost.size());

  CpModelBuilder model;
  std::vector<IntVar> task;  // task[w] is the task given to worker w.
  std::vector<LinearExpr> task_exprs;
  LinearExpr total;
  for (int w = 0; w < n; ++w) {
    task.push_back(model.NewIntVar(Domain(0, n - 1)));
    task_exprs.push_back(task.back());
    // The element constraint looks up the cost at a variable position. It takes
    // a constant array here, so the cost table needs no IntVars.
    IntVar price = model.NewIntVar(Domain(0, 100));
    model.AddElement(task[w], cost[w], price);
    total += price;
  }
  model.AddAllDifferent(task_exprs);
  model.Minimize(total);

  const CpSolverResponse response = Solve(model.Build());
  std::cout << "Status: " << CpSolverStatus_Name(response.status()) << "\n";
  if (response.status() != CpSolverStatus::OPTIMAL) return 0;
  std::cout << "Minimum cost: " << static_cast<int64_t>(response.objective_value()) << "\n";
  for (int w = 0; w < n; ++w) {
    std::cout << "worker " << w << " -> task " << SolutionIntegerValue(response, task[w]) << "\n";
  }
  return 0;
}
