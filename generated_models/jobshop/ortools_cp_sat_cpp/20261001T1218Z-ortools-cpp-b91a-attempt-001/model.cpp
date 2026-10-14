#include <map>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Job shop: each job is a sequence of tasks that must run in the given order,
// each task on one specific machine for a fixed duration. A machine does one
// task at a time and a task runs to completion without interruption.
// Minimize the makespan, the time at which all jobs have finished.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  // jobs_data[job][task] = [machine_id, duration]. Jobs may have different
  // numbers of tasks, so the data is read straight from the JSON.
  const json& jobs_data = instance.at("jobs_data");
  const int n_jobs = static_cast<int>(jobs_data.size());

  // No time can exceed the total of all durations.
  int64_t max_duration = 0;
  for (const json& job : jobs_data)
    for (const json& task : job) max_duration += task.at(1).get<int64_t>();

  std::vector<std::vector<IntVar>> end_times(n_jobs);
  // The tasks that run on each machine, as intervals for the no-overlap constraint.
  std::map<int64_t, std::vector<IntervalVar>> machine_tasks;

  for (int job_id = 0; job_id < n_jobs; ++job_id) {
    const json& job = jobs_data[job_id];
    for (int task_id = 0; task_id < static_cast<int>(job.size()); ++task_id) {
      const int64_t machine = job[task_id].at(0).get<int64_t>();
      const int64_t duration = job[task_id].at(1).get<int64_t>();

      // A task starts at some time, runs for its duration and then ends.
      const IntVar start = model.NewIntVar(Domain(0, max_duration));
      const IntVar end = model.NewIntVar(Domain(0, max_duration));
      const IntervalVar task = model.NewIntervalVar(start, duration, end);
      end_times[job_id].push_back(end);
      machine_tasks[machine].push_back(task);

      // No task of a job can start before the previous task of that job ends.
      if (task_id > 0) {
        model.AddGreaterOrEqual(start, end_times[job_id][task_id - 1]);
      }
    }
  }

  // A machine can only work on one task at a time.
  for (const auto& entry : machine_tasks) model.AddNoOverlap(entry.second);

  // The makespan is the latest end of any task; minimize it.
  std::vector<LinearExpr> all_ends;
  for (const auto& job_ends : end_times)
    for (const IntVar& e : job_ends) all_ends.push_back(e);
  const IntVar makespan = model.NewIntVar(Domain(0, max_duration));
  model.AddMaxEquality(makespan, all_ends);
  model.Minimize(makespan);

  outputs = {{"makespan", makespan.index()}};
}
