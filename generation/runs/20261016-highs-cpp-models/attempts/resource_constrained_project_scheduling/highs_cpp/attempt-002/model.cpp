// Resource-constrained project scheduling: jobs with durations, precedence arcs between
// jobs, and renewable resources with limited capacity. Find the start time of every job
// that minimises the makespan, the finish time of the last job. Start times are integers from 0.
// Time-indexed encoding: a binary per (job, start slot) links each start time to the slots it can take.
// The start-slot windows are narrowed from the precedence arcs (earliest and latest start), so
// fewer slot binaries are needed.
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

  // Horizon: running the jobs one after another finishes at the total duration, so an optimal
  // makespan is at most H, and every job of an optimal schedule finishes by H.
  int H = 0;
  for (int d : durations) H += d;

  // Earliest start: the longest chain of predecessor durations leading into the job.
  // Latest start: H minus the job's duration and the longest chain of successor durations after it.
  std::vector<int> earliest(n, 0), tail(n, 0);
  for (int pass = 0; pass < n; ++pass) {
    for (const auto& arc : arcs) {
      const int pred = arc[0], succ = arc[1];
      earliest[succ] = std::max(earliest[succ], earliest[pred] + durations[pred]);
      tail[pred] = std::max(tail[pred], tail[succ] + durations[succ]);
    }
  }
  int critical = 0;
  for (int j = 0; j < n; ++j) critical = std::max(critical, earliest[j] + durations[j]);

  // start[j] is the start time of job j, between its earliest and latest start.
  std::vector<Lin> start(n);
  // slot[j][t - earliest[j]] = 1 when job j starts at time t.
  std::vector<std::vector<Lin>> slot(n);
  for (int j = 0; j < n; ++j) {
    const int latest = H - durations[j] - tail[j];
    start[j] = new_var(h, earliest[j], latest, true);
    for (int t = earliest[j]; t <= latest; ++t) slot[j].push_back(new_var(h, 0, 1, true));

    // each job starts at exactly one time
    Lin one_slot;
    for (const Lin& s : slot[j]) one_slot = one_slot + s;
    add_row(h, one_slot, 1, 1);

    // the start time is the slot the job starts at
    Lin start_from_slots = start[j];
    for (int t = earliest[j]; t <= latest; ++t)
      start_from_slots = start_from_slots - static_cast<double>(t) * slot[j][t - earliest[j]];
    add_row(h, start_from_slots, 0, 0);
  }

  // the makespan is the latest finish time of any job, and at least the critical path length
  Lin makespan = new_var(h, critical, H, true);
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
        // job j runs at time t when it starts in the window (t - d_j, t], within its own slots
        const int first = std::max(earliest[j], t - durations[j] + 1);
        const int last = std::min(t, H - durations[j] - tail[j]);
        if (first > last) continue;
        possible_need += need;
        for (int tau = first; tau <= last; ++tau)
          usage = usage + static_cast<double>(need) * slot[j][tau - earliest[j]];
      }
      if (possible_need > capacities[r]) add_row(h, usage, -kHighsInf, capacities[r]);
    }
  }

  out.add("start_time", start);
  out.minimize(makespan);
}
