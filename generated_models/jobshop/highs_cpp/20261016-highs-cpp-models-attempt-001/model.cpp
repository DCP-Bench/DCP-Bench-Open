// Job shop: several jobs, each a fixed sequence of tasks, each task processed on one specific machine
// for a fixed duration. Minimise the makespan, the total time taken to complete all jobs.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const json& jobs = instance.at("jobs_data");  // jobs_data[j][k] = [machine, duration] of task k of job j

  // The horizon is the total work of all tasks. A schedule without idle time ends by then, so every
  // start time lies in 0..H, and H is a valid big-M for every machine disjunction below.
  int horizon = 0;
  for (const json& job : jobs)
    for (const json& task : job) horizon += task.at(1).get<int>();
  const double big_m = horizon;

  // The makespan is an integer in 0..H.
  dcp::Lin makespan = dcp::new_var(h, 0, big_m);

  // The start time of each task: start[j][k] lies in 0..H - duration, so the task ends by H.
  std::vector<std::vector<dcp::Lin>> start;
  for (const json& job : jobs) {
    std::vector<dcp::Lin> starts;
    for (const json& task : job) starts.push_back(dcp::new_var(h, 0, big_m - task.at(1).get<int>()));
    start.push_back(starts);
  }

  // The tasks of a job run in the order given: each task is completed before the next one starts.
  for (size_t j = 0; j < jobs.size(); ++j)
    for (size_t k = 0; k + 1 < jobs[j].size(); ++k) {
      int duration = jobs[j][k].at(1).get<int>();
      dcp::add_row(h, start[j][k + 1] - start[j][k], duration, kHighsInf);
    }

  // The makespan is no earlier than the completion of the last task of every job.
  for (size_t j = 0; j < jobs.size(); ++j) {
    if (jobs[j].empty()) continue;
    size_t last = jobs[j].size() - 1;
    int duration = jobs[j][last].at(1).get<int>();
    dcp::add_row(h, makespan - start[j][last], duration, kHighsInf);
  }

  // A machine works on one task at a time. For two tasks p and q on the same machine, either p is
  // completed before q starts, or q is completed before p starts. The binary `p_first` picks the order,
  // and big-M = H makes the unchosen order's row hold.
  struct Task {
    size_t job, index;
    int machine, duration;
  };
  std::vector<Task> tasks;
  for (size_t j = 0; j < jobs.size(); ++j)
    for (size_t k = 0; k < jobs[j].size(); ++k)
      tasks.push_back({j, k, jobs[j][k].at(0).get<int>(), jobs[j][k].at(1).get<int>()});

  for (size_t a = 0; a < tasks.size(); ++a)
    for (size_t b = a + 1; b < tasks.size(); ++b) {
      const Task& p = tasks[a];
      const Task& q = tasks[b];
      if (p.machine != q.machine) continue;
      dcp::Lin sp = start[p.job][p.index];
      dcp::Lin sq = start[q.job][q.index];
      dcp::Lin p_first = dcp::new_var(h, 0, 1);
      // p_first = 1: p is completed before q starts, start_p + duration_p <= start_q.
      dcp::add_row(h, sp - sq + big_m * p_first, -kHighsInf, big_m - p.duration);
      // p_first = 0: q is completed before p starts, start_q + duration_q <= start_p.
      dcp::add_row(h, sq - sp - big_m * p_first, -kHighsInf, -q.duration);
    }

  out.minimize(makespan);
  out.add("makespan", makespan);
}
