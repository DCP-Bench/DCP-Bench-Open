#include <numeric>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Resource-constrained project scheduling: schedule jobs, each with a
// duration and a demand on several renewable resources, so that precedence
// relations between jobs hold, no resource is used beyond its capacity at any
// time, and the project finishes as early as possible.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<int64_t> durations =
      instance.at("durations_data").get<std::vector<int64_t>>();
  // resource_needs[j][r] is how much of resource r job j uses while it runs.
  const std::vector<std::vector<int64_t>> resource_needs =
      instance.at("resource_needs_data").get<std::vector<std::vector<int64_t>>>();
  const std::vector<int64_t> resource_capacities =
      instance.at("resource_capacities_data").get<std::vector<int64_t>>();
  // Each pair [a, b] says job b cannot start before job a has finished.
  const std::vector<std::vector<int>> successors_link =
      instance.at("successors_link_data").get<std::vector<std::vector<int>>>();

  const int nb_resource = static_cast<int>(resource_capacities.size());
  const int nb_jobs = static_cast<int>(durations.size());
  // No job can start later than the sum of all durations (the reference's bound).
  const int64_t max_duration = std::accumulate(durations.begin(), durations.end(), int64_t{0});

  // start_time[j] is the start time of job j.
  std::vector<IntVar> start_time;
  for (int j = 0; j < nb_jobs; ++j) start_time.push_back(model.NewIntVar(Domain(0, max_duration)));

  // Precedence: a job starts only after its predecessor has finished.
  for (const std::vector<int>& link : successors_link) {
    model.AddGreaterOrEqual(start_time[link[1]], start_time[link[0]] + durations[link[0]]);
  }

  // Each job occupies the interval [start, start + duration).
  std::vector<IntervalVar> job_interval;
  for (int j = 0; j < nb_jobs; ++j)
    job_interval.push_back(model.NewFixedSizeIntervalVar(start_time[j], durations[j]));

  // Resource capacity: at every time the jobs running together need no more
  // of a resource than its capacity.
  for (int r = 0; r < nb_resource; ++r) {
    CumulativeConstraint usage = model.AddCumulative(resource_capacities[r]);
    for (int j = 0; j < nb_jobs; ++j) usage.AddDemand(job_interval[j], resource_needs[j][r]);
  }

  // The makespan is the latest start time over all jobs (as in the reference,
  // where the last job is a dummy with no duration); minimize it.
  std::vector<LinearExpr> starts(start_time.begin(), start_time.end());
  const IntVar makespan = model.NewIntVar(Domain(0, max_duration));
  model.AddMaxEquality(makespan, starts);
  model.Minimize(makespan);

  json out = json::array();
  for (const IntVar& v : start_time) out.push_back(v.index());
  outputs = {{"start_time", out}};
}
