#include <numeric>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Flow shop scheduling: every job visits the machines in the same order
// (machine 1 to machine M) and all machines see the jobs in the same sequence.
// Find the job sequence that minimizes the makespan, the time at which all
// jobs have been processed.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n_jobs = static_cast<int>(instance.at("jobs").size());
  const int n_machines = static_cast<int>(instance.at("machines").size());
  // process_time[j][m] is the time job j needs on machine m.
  const std::vector<std::vector<int64_t>> process_time =
      instance.at("process_time").get<std::vector<std::vector<int64_t>>>();

  // No time can exceed the total of all processing times.
  int64_t max_duration = 0;
  for (const auto& row : process_time) max_duration += std::accumulate(row.begin(), row.end(), int64_t{0});

  // sequence[k] is the job processed k-th.
  std::vector<IntVar> sequence;
  for (int k = 0; k < n_jobs; ++k) sequence.push_back(model.NewIntVar(Domain(0, n_jobs - 1)));

  // start_times[k][m] and end_times[k][m]: when the k-th job of the sequence
  // starts and finishes on machine m.
  std::vector<std::vector<IntVar>> start_times(n_jobs), end_times(n_jobs);
  for (int k = 0; k < n_jobs; ++k) {
    for (int m = 0; m < n_machines; ++m) {
      start_times[k].push_back(model.NewIntVar(Domain(0, max_duration)));
      end_times[k].push_back(model.NewIntVar(Domain(0, max_duration)));
    }
  }

  // time_on[m][j] is the processing time of job j on machine m, so it can be
  // indexed by the job variable sequence[k] with an element constraint.
  std::vector<std::vector<int64_t>> time_on(n_machines, std::vector<int64_t>(n_jobs));
  for (int m = 0; m < n_machines; ++m)
    for (int j = 0; j < n_jobs; ++j) time_on[m][j] = process_time[j][m];

  // Every job appears exactly once in the sequence.
  model.AddAllDifferent(sequence);

  for (int k = 0; k < n_jobs; ++k) {
    for (int m = 0; m < n_machines; ++m) {
      // A job occupies a machine for its processing time on that machine.
      const IntVar duration = model.NewIntVar(Domain(0, max_duration));
      model.AddElement(sequence[k], time_on[m], duration);
      model.AddEquality(end_times[k][m], start_times[k][m] + duration);
      // A job cannot start on machine m before it has finished on machine m-1.
      if (m > 0) model.AddGreaterOrEqual(start_times[k][m], end_times[k][m - 1]);
      // The k-th job cannot start on machine m before the (k-1)-th has left it.
      if (k > 0) model.AddGreaterOrEqual(start_times[k][m], end_times[k - 1][m]);
    }
  }

  // The makespan is the latest completion over all jobs and machines; minimize it.
  std::vector<LinearExpr> all_ends;
  for (int k = 0; k < n_jobs; ++k)
    for (int m = 0; m < n_machines; ++m) all_ends.push_back(end_times[k][m]);
  const IntVar makespan = model.NewIntVar(Domain(0, max_duration));
  model.AddMaxEquality(makespan, all_ends);
  model.Minimize(makespan);

  outputs = {{"makespan", makespan.index()}};
}
