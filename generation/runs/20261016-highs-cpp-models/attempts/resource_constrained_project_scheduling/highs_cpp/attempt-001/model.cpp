// Resource-constrained project scheduling: jobs with durations, precedence arcs between
// jobs, and renewable resources with limited capacity. Find the start time of every job
// that minimises the makespan, the finish time of the last job. Start times are integers from 0.
// Time-indexed encoding: a binary per (job, start slot) links each start time to the slots it can take.
#include <algorithm>
#include <vector>

#include "dcp.h"

using dcp::Lin;
using dcp::add_row;
using dcp::new_var;

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const std::vector<int> durations = instance.at("durations_data").get<std::vector<int>>();
  const std::vector<int> capacities = instance.at("resource_capacities_data").get<std::vector<int>>();
  const std::vector<std::vector<int>> needs =
      instance.at("resource_needs_data").get<std::vector<std::vector<int>>>();
  const std::vector<std::vector<int>> arcs =
      instance.at("successors_link_data").get<std::vector<std::vector<int>>>();
  const int n = static_cast<int>(durations.size());
  const int R = static_cast<int>(capacities.size());

  // Horizon: running the jobs one after another (in any precedence-respecting order) finishes at
  // the total duration, so an optimal makespan is at most H, and every job starts by H - its duration.
  int H = 0;
  for (int d : durations) H += d;

  // start[j] is the start time of job j, from 0 to H - d_j.
  std::vector<Lin> start(n);
  // slot[j][t] = 1 when job j starts at time t (only t in 0..H - d_j).
  std::vector<std::vector<Lin>> slot(n);
  for (int j = 0; j < n; ++j) {
    const int latest = H - durations[j];
    start[j] = new_var(h, 0, latest, true);
    for (int t = 0; t <= latest; ++t) slot[j].push_back(new_var(h, 0, 1, true));

    // each job starts at exactly one time
    Lin one_slot;
    for (int t = 0; t <= latest; ++t) one_slot = one_slot + slot[j][t];
    add_row(h, one_slot, 1, 1);

    // the start time is the slot the job starts at
    Lin start_from_slots = start[j];
    for (int t = 0; t <= latest; ++t) start_from_slots = start_from_slots - static_cast<double>(t) * slot[j][t];
    add_row(h, start_from_slots, 0, 0);
  }

  // the makespan is the latest finish time of any job
  Lin makespan = new_var(h, 0, H, true);
  for (int j = 0; j < n; ++j) {
    // the makespan is at least the finish time of job j
    add_row(h, makespan - start[j], durations[j], kHighsInf);
  }

  // precedence: a job starts only after each of its predecessors has finished
  for (const auto& arc : arcs) {
    const int pred = arc[0], succ = arc[1];
    add_row(h, start[succ] - start[pred], durations[pred], kHighsInf);
  }

  // resource capacity: at every time, the jobs running use no more than the capacity of each resource
  for (int r = 0; r < R; ++r) {
    for (int t = 0; t < H; ++t) {
      Lin usage;
      int possible_need = 0;
      for (int j = 0; j < n; ++j) {
        const int need = needs[j][r];
        if (need == 0 || durations[j] == 0) continue;
        // job j runs at time t when it starts in the window (t - d_j, t]
        const int first = std::max(0, t - durations[j] + 1);
        const int last = std::min(t, H - durations[j]);
        if (first > last) continue;
        possible_need += need;
        for (int tau = first; tau <= last; ++tau) usage = usage + static_cast<double>(need) * slot[j][tau];
      }
      if (possible_need > capacities[r]) add_row(h, usage, -kHighsInf, capacities[r]);
    }
  }

  out.add("start_time", start);
  out.minimize(makespan);
}
