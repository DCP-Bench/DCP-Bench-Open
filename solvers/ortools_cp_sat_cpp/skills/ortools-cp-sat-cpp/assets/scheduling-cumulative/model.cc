// Schedule 5 tasks with precedences on a shared resource of capacity 3, and
// minimise the makespan (the finish time of the last task).
#include <cstdint>
#include <iostream>
#include <vector>

#include "ortools/sat/cp_model.h"
#include "ortools/sat/cp_model_solver.h"

using namespace operations_research;
using namespace operations_research::sat;

int main() {
  const std::vector<int64_t> duration = {3, 2, 4, 2, 3};
  const std::vector<int64_t> demand = {2, 1, 2, 1, 2};
  const int64_t capacity = 3;
  // Pairs (a, b): task a must finish before task b starts.
  const std::vector<std::pair<int, int>> precedence = {{0, 2}, {1, 3}, {2, 4}};
  const int n = static_cast<int>(duration.size());

  int64_t horizon = 0;
  for (int64_t d : duration) horizon += d;

  CpModelBuilder model;
  std::vector<IntVar> start;
  auto cumulative = model.AddCumulative(capacity);
  for (int t = 0; t < n; ++t) {
    start.push_back(model.NewIntVar(Domain(0, horizon - duration[t])));
    IntervalVar interval = model.NewFixedSizeIntervalVar(start[t], duration[t]);
    cumulative.AddDemand(interval, demand[t]);
  }
  for (const auto& [a, b] : precedence) {
    model.AddGreaterOrEqual(start[b], start[a] + duration[a]);
  }

  IntVar makespan = model.NewIntVar(Domain(0, horizon));
  for (int t = 0; t < n; ++t) {
    model.AddGreaterOrEqual(makespan, start[t] + duration[t]);
  }
  model.Minimize(makespan);

  const CpSolverResponse response = Solve(model.Build());
  std::cout << "Status: " << CpSolverStatus_Name(response.status()) << "\n";
  if (response.status() != CpSolverStatus::OPTIMAL) return 0;
  std::cout << "Makespan: " << SolutionIntegerValue(response, makespan) << "\n";
  for (int t = 0; t < n; ++t) {
    std::cout << "task " << t << " starts at " << SolutionIntegerValue(response, start[t]) << "\n";
  }
  return 0;
}
