// Permutation flow shop: choose the order of the jobs, each processed on machines 1..M in series, to minimize the makespan.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<std::vector<int>> process_time = instance.at("process_time").get<std::vector<std::vector<int>>>();
  int n = static_cast<int>(process_time.size());
  int machines = static_cast<int>(process_time[0].size());

  // an upper bound on the makespan is running the jobs one after the other
  int horizon = 0;
  for (auto& row : process_time)
    for (int p : row) horizon += p;

  // sequence[k] is the job processed k-th (the same sequence on every machine)
  vec<IntVar*> sequence;
  createVars(sequence, n, 0, n - 1, true);
  all_different(sequence);

  // duration[k][m] is the time the k-th job of the sequence needs on machine m
  // start[k][m] is the time at which the k-th job of the sequence starts on machine m
  vec<vec<IntVar*>> duration(n), start(n);
  for (int k = 0; k < n; ++k)
    for (int m = 0; m < machines; ++m) {
      int lo = process_time[0][m], hi = process_time[0][m];
      vec<int> column;
      for (int j = 0; j < n; ++j) {
        column.push(process_time[j][m]);
        lo = std::min(lo, process_time[j][m]);
        hi = std::max(hi, process_time[j][m]);
      }
      IntVar* d = newIntVar(lo, hi);
      // the time required to process job j on machine m is process_time[j][m]
      array_int_element(sequence[k], column, d);
      duration[k].push(d);
      start[k].push(newIntVar(0, horizon));
    }

  for (int k = 0; k < n; ++k)
    for (int m = 0; m < machines; ++m) {
      // a machine processes one job at a time: the next job of the sequence starts after the previous one finishes
      if (k > 0) {
        IntVar* prev_end = newIntVar(0, horizon);
        int_plus(start[k - 1][m], duration[k - 1][m], prev_end);
        int_rel(start[k][m], IRT_GE, prev_end);
      }
      // a job goes to machine m+1 only when machine m has finished it
      if (m > 0) {
        IntVar* done = newIntVar(0, horizon);
        int_plus(start[k][m - 1], duration[k][m - 1], done);
        int_rel(start[k][m], IRT_GE, done);
      }
    }

  // the makespan is the time when the last job has been processed on the last machine
  IntVar* makespan = newIntVar(0, horizon);
  int_plus(start[n - 1][machines - 1], duration[n - 1][machines - 1], makespan);

  // minimize the makespan
  branch(sequence, VAR_INORDER, VAL_MIN);
  optimize(makespan, OPT_MIN);
  outputs = {{"makespan", dcp::out(makespan)}};
}
