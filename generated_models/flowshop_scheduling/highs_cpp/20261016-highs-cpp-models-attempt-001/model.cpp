// Flow shop scheduling: n jobs go through M machines in series, in the same job
// order on every machine. Each machine works on one job at a time, and a job
// starts on a machine only after it has finished on the previous machine. Find
// the job sequence that minimises the makespan, the time when all jobs have been
// processed on the last machine. Output the optimal makespan.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int n = static_cast<int>(instance.at("jobs").size());
  const int M = static_cast<int>(instance.at("machines").size());
  const json& pt = instance.at("process_time");

  // the sum of all processing times bounds every completion time
  double horizon = 0;
  for (int j = 0; j < n; ++j)
    for (int m = 0; m < M; ++m) horizon += pt[j][m].get<double>();

  // x[j][p] = 1 when job j is at position p of the sequence
  std::vector<std::vector<dcp::Lin>> x(n, std::vector<dcp::Lin>(n));
  for (int j = 0; j < n; ++j)
    for (int p = 0; p < n; ++p) x[j][p] = dcp::new_var(h, 0, 1);

  // every job takes exactly one position
  for (int j = 0; j < n; ++j) {
    dcp::Lin e;
    for (int p = 0; p < n; ++p) e = e + x[j][p];
    dcp::add_row(h, e, 1, 1);
  }
  // every position holds exactly one job
  for (int p = 0; p < n; ++p) {
    dcp::Lin e;
    for (int j = 0; j < n; ++j) e = e + x[j][p];
    dcp::add_row(h, e, 1, 1);
  }

  // C[p][m] = completion time on machine m of the job at position p
  std::vector<std::vector<dcp::Lin>> C(n, std::vector<dcp::Lin>(M));
  for (int p = 0; p < n; ++p)
    for (int m = 0; m < M; ++m) C[p][m] = dcp::new_var(h, 0, horizon);

  // processing time of the job at position p on machine m
  std::vector<std::vector<dcp::Lin>> d(n, std::vector<dcp::Lin>(M));
  for (int p = 0; p < n; ++p)
    for (int m = 0; m < M; ++m) {
      dcp::Lin e;
      for (int j = 0; j < n; ++j) e = e + pt[j][m].get<double>() * x[j][p];
      d[p][m] = e;
    }

  // a job finishes on a machine only after its start: after the previous job on
  // the same machine has left it, plus its own processing time
  for (int p = 1; p < n; ++p)
    for (int m = 0; m < M; ++m)
      dcp::add_row(h, C[p][m] - C[p - 1][m] - d[p][m], 0, kHighsInf);

  // a job finishes on a machine only after it has been processed on the previous machine
  for (int p = 0; p < n; ++p)
    for (int m = 1; m < M; ++m)
      dcp::add_row(h, C[p][m] - C[p][m - 1] - d[p][m], 0, kHighsInf);

  // the first job on the first machine starts at time zero
  dcp::add_row(h, C[0][0] - d[0][0], 0, kHighsInf);

  out.add("makespan", C[n - 1][M - 1]);
  out.minimize(C[n - 1][M - 1]);
}
