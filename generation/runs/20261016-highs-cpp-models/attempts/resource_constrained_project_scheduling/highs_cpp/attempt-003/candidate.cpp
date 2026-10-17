// Resource-constrained project scheduling: jobs with durations, precedence arcs between
// jobs, and renewable resources with limited capacity. Find the start time of every job
// that minimises the makespan, the finish time of the last job. Start times are integers from 0.
// Time-indexed encoding: a binary per (job, start slot) links each start time to the slots it can take.
// The horizon is tightened from the instance: a serial schedule gives an upper bound on the makespan,
// and the precedence arcs and resource energy give lower bounds, so fewer slot binaries are needed.
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

  int total = 0;
  for (int d : durations) total += d;

  // Predecessor and successor lists, and a topological order of the jobs (Kahn's algorithm).
  std::vector<std::vector<int>> preds(n), succs(n);
  std::vector<int> indegree(n, 0);
  for (const auto& arc : arcs) {
    preds[arc[1]].push_back(arc[0]);
    succs[arc[0]].push_back(arc[1]);
    indegree[arc[1]]++;
  }
  std::vector<int> order, ready;
  for (int j = 0; j < n; ++j)
    if (indegree[j] == 0) ready.push_back(j);
  while (!ready.empty()) {
    const int j = ready.back();
    ready.pop_back();
    order.push_back(j);
    for (int k : succs[j])
      if (--indegree[k] == 0) ready.push_back(k);
  }

  // Serial schedule: in topological order, each job starts at the earliest time its predecessors
  // have finished and its resources are free. Its makespan is an upper bound on the optimum.
  std::vector<std::vector<int>> load(R, std::vector<int>(total + 1, 0));
  std::vector<int> begin(n, 0);
  int upper = 0;
  for (int j : order) {
    int est = 0;
    for (int p : preds[j]) est = std::max(est, begin[p] + durations[p]);
    int s = est;
    for (; s + durations[j] <= total; ++s) {
      bool fits = true;
      for (int t = s; fits && t < s + durations[j]; ++t)
        for (int r = 0; r < R; ++r)
          if (load[r][t] + needs[j][r] > capacities[r]) fits = false;
      if (fits) break;
    }
    if (s + durations[j] > total) throw std::runtime_error("no feasible serial schedule");
    begin[j] = s;
    for (int t = s; t < s + durations[j]; ++t)
      for (int r = 0; r < R; ++r) load[r][t] += needs[j][r];
    upper = std::max(upper, s + durations[j]);
  }
  const int H = upper;

  // Lower bound on the makespan: the longest precedence chain, and for each resource its total
  // work divided by its capacity.
  std::vector<int> earliest(n, 0), tail(n, 0);
  for (int pass = 0; pass < n; ++pass) {
    for (const auto& arc : arcs) {
      const int pred = arc[0], succ = arc[1];
      earliest[succ] = std::max(earliest[succ], earliest[pred] + durations[pred]);
      tail[pred] = std::max(tail[pred], tail[succ] + durations[succ]);
    }
  }
  int lower = 0;
  for (int j = 0; j < n; ++j) lower = std::max(lower, earliest[j] + durations[j]);
  for (int r = 0; r < R; ++r) {
    long long work = 0;
    for (int j = 0; j < n; ++j) work += static_cast<long long>(needs[j][r]) * durations[j];
    if (capacities[r] > 0) lower = std::max(lower, static_cast<int>((work + capacities[r] - 1) / capacities[r]));
  }

  // start[j] is the start time of job j, between its earliest start and its latest start
  // (the latest finish H, less the job's own duration and the chain of successors after it).
  std::vector<Lin> start(n);
  // slot[j][t - earliest[j]] = 1 when job j starts at time t.
  std::vector<std::vector<Lin>> slot(n);
  std::vector<int> latest(n);
  for (int j = 0; j < n; ++j) {
    latest[j] = H - durations[j] - tail[j];
    start[j] = new_var(h, earliest[j], latest[j], true);
    for (int t = earliest[j]; t <= latest[j]; ++t) slot[j].push_back(new_var(h, 0, 1, true));

    // each job starts at exactly one time
    Lin one_slot;
    for (const Lin& s : slot[j]) one_slot = one_slot + s;
    add_row(h, one_slot, 1, 1);

    // the start time is the slot the job starts at
    Lin start_from_slots = start[j];
    for (int t = earliest[j]; t <= latest[j]; ++t)
      start_from_slots = start_from_slots - static_cast<double>(t) * slot[j][t - earliest[j]];
    add_row(h, start_from_slots, 0, 0);
  }

  // the makespan is the latest finish time of any job
  Lin makespan = new_var(h, lower, H, true);
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
        const int last = std::min(t, latest[j]);
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
