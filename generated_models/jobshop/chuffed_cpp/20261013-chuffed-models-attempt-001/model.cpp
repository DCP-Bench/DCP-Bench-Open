// Job shop: schedule the tasks of each job on machines so that the total length (makespan) is minimized.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // jobs_data[j] is the sequence of tasks of job j, each task is [machine, duration]
  const json& jobs = instance.at("jobs_data");
  int num_jobs = static_cast<int>(jobs.size());
  int num_machines = 0;
  int horizon = 0;  // the sum of all durations is an upper bound on the makespan
  for (int j = 0; j < num_jobs; ++j) {
    for (const json& task : jobs[j]) {
      int machine = task[0];
      if (machine + 1 > num_machines) num_machines = machine + 1;
      horizon += task[1].get<int>();
    }
  }

  // start[j][k] is the start time of the k-th task of job j
  std::vector<std::vector<IntVar*>> start(num_jobs);
  vec<IntVar*> all_starts;
  std::vector<vec<IntVar*>> machine_starts(num_machines);
  std::vector<vec<int>> machine_durations(num_machines);
  IntVar* makespan = newIntVar(0, horizon);
  for (int j = 0; j < num_jobs; ++j) {
    for (size_t k = 0; k < jobs[j].size(); ++k) {
      int machine = jobs[j][k][0];
      int duration = jobs[j][k][1];
      IntVar* s = newIntVar(0, horizon - duration);
      start[j].push_back(s);
      all_starts.push(s);
      machine_starts[machine].push(s);
      machine_durations[machine].push(duration);
      // the makespan is the time it takes for all jobs to be completed
      int_rel(makespan, IRT_GE, s, duration);
    }
  }

  // no task for a job can be started until the previous task for that job is completed
  for (int j = 0; j < num_jobs; ++j) {
    for (size_t k = 1; k < jobs[j].size(); ++k) {
      int prev_duration = jobs[j][k - 1][1];
      int_rel(start[j][k], IRT_GE, start[j][k - 1], prev_duration);
    }
  }

  // a machine can only work on one task at a time (a started task runs to completion)
  for (int m = 0; m < num_machines; ++m) {
    if (machine_starts[m].size() > 1) disjunctive(machine_starts[m], machine_durations[m]);
  }

  // minimize the makespan; schedule the earliest-startable task first
  branch(all_starts, VAR_MIN_MIN, VAL_MIN);
  optimize(makespan, OPT_MIN);

  outputs = {{"makespan", dcp::out(makespan)}};
}
