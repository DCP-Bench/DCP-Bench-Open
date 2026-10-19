// Job shop with 3 jobs on 3 machines: each job visits its machines in order,
// and each machine runs one operation at a time (a unary, no-overlap resource).
// Minimise the makespan. One AddNoOverlap call per machine.
#include <cstdint>
#include <iostream>
#include <vector>

#include "ortools/sat/cp_model.h"
#include "ortools/sat/cp_model_solver.h"

using namespace operations_research;
using namespace operations_research::sat;

int main() {
  // jobs[j][k] = {machine, duration} of operation k of job j, in technological order.
  const std::vector<std::vector<std::pair<int, int64_t>>> jobs = {
      {{0, 3}, {1, 2}, {2, 2}},
      {{0, 2}, {2, 1}, {1, 4}},
      {{1, 4}, {2, 3}, {0, 2}},
  };
  const int num_machines = 3;

  int64_t horizon = 0;
  for (const auto& job : jobs) {
    for (const auto& [machine, duration] : job) horizon += duration;
  }

  CpModelBuilder model;
  std::vector<std::vector<IntVar>> start(jobs.size());
  std::vector<std::vector<IntervalVar>> on_machine(num_machines);
  for (size_t j = 0; j < jobs.size(); ++j) {
    for (size_t k = 0; k < jobs[j].size(); ++k) {
      const auto [machine, duration] = jobs[j][k];
      start[j].push_back(model.NewIntVar(Domain(0, horizon - duration)));
      on_machine[machine].push_back(
          model.NewFixedSizeIntervalVar(start[j][k], duration));
      if (k > 0) {
        // The previous operation of the same job must finish first.
        model.AddGreaterOrEqual(start[j][k],
                                start[j][k - 1] + jobs[j][k - 1].second);
      }
    }
  }
  // No two operations on one machine overlap. Each machine gets its own call:
  // one call over all intervals would forbid overlap between machines too.
  for (const auto& intervals : on_machine) model.AddNoOverlap(intervals);

  IntVar makespan = model.NewIntVar(Domain(0, horizon));
  for (size_t j = 0; j < jobs.size(); ++j) {
    const size_t last = jobs[j].size() - 1;
    model.AddGreaterOrEqual(makespan, start[j][last] + jobs[j][last].second);
  }
  model.Minimize(makespan);

  const CpSolverResponse response = Solve(model.Build());
  std::cout << "Status: " << CpSolverStatus_Name(response.status()) << "\n";
  if (response.status() != CpSolverStatus::OPTIMAL) return 0;
  std::cout << "Makespan: " << SolutionIntegerValue(response, makespan) << "\n";
  for (size_t j = 0; j < jobs.size(); ++j) {
    std::cout << "job " << j << " starts:";
    for (size_t k = 0; k < jobs[j].size(); ++k) {
      std::cout << " " << SolutionIntegerValue(response, start[j][k]);
    }
    std::cout << "\n";
  }
  return 0;
}
