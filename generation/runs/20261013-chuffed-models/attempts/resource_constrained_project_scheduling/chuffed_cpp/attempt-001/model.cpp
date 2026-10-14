// Resource-constrained project scheduling: start every job so that precedences and resource capacities hold and the makespan is minimal.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<int> duration = instance.at("durations_data").get<std::vector<int>>();
  std::vector<std::vector<int>> need = instance.at("resource_needs_data").get<std::vector<std::vector<int>>>();
  std::vector<int> capacity = instance.at("resource_capacities_data").get<std::vector<int>>();
  std::vector<std::vector<int>> links = instance.at("successors_link_data").get<std::vector<std::vector<int>>>();
  int num_jobs = static_cast<int>(duration.size());
  int num_resources = static_cast<int>(capacity.size());

  // the project cannot take longer than the sum of all durations
  int horizon = 0;
  for (int d : duration) horizon += d;

  // start[j] is the start time of job j
  vec<IntVar*> start;
  createVars(start, num_jobs, 0, horizon);

  // precedence: a job starts only after each of its predecessors has finished
  for (const auto& link : links) {
    int i = link[0];
    int j = link[1];
    // start[i] + duration[i] <= start[j]
    int_rel(start[i], IRT_LE, start[j], -duration[i]);
  }

  // resources: at every time the jobs running on a resource need no more than its capacity
  for (int k = 0; k < num_resources; ++k) {
    vec<int> dur;
    vec<int> demand;
    for (int j = 0; j < num_jobs; ++j) {
      dur.push(duration[j]);
      demand.push(need[j][k]);
    }
    cumulative(start, dur, demand, capacity[k]);
  }

  // the makespan is the finish time of the last job
  IntVar* makespan = newIntVar(0, horizon);
  for (int j = 0; j < num_jobs; ++j) {
    // start[j] + duration[j] <= makespan
    int_rel(start[j], IRT_LE, makespan, -duration[j]);
  }

  // schedule the jobs in order of their start times, earliest first
  branch(start, VAR_MIN_MIN, VAL_MIN);

  // minimize the makespan
  optimize(makespan, OPT_MIN);

  json start_times = json::array();
  for (int j = 0; j < num_jobs; ++j) start_times.push_back(dcp::out(start[j]));
  outputs = {{"start_time", start_times}};
}
