// csplib_007_all_interval: find a series x of the pitch-classes 0..n-1, each occurring exactly once,
// whose neighbouring intervals |x[i+1] - x[i]| cover each of the values 1..n-1 exactly once.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n").get<int>();

  // the pitch-class at each position of the series, 0..n-1
  std::vector<dcp::Lin> x;
  for (int i = 0; i < n; i++) x.push_back(dcp::new_var(h, 0, n - 1));

  // the interval between neighbouring positions i and i+1, 1..n-1
  std::vector<dcp::Lin> diffs;
  for (int i = 0; i < n - 1; i++) diffs.push_back(dcp::new_var(h, 1, n - 1));

  // y[i][v] = 1 when position i holds pitch-class v
  std::vector<std::vector<dcp::Lin>> y(n, std::vector<dcp::Lin>(n));
  for (int i = 0; i < n; i++)
    for (int v = 0; v < n; v++) y[i][v] = dcp::new_var(h, 0, 1);

  // each position holds exactly one pitch-class
  for (int i = 0; i < n; i++) {
    dcp::Lin s = 0.0;
    for (int v = 0; v < n; v++) s = s + y[i][v];
    dcp::add_row(h, s, 1, 1);
  }

  // each pitch-class occurs in exactly one position
  for (int v = 0; v < n; v++) {
    dcp::Lin s = 0.0;
    for (int i = 0; i < n; i++) s = s + y[i][v];
    dcp::add_row(h, s, 1, 1);
  }

  // the pitch-class of each position is the value chosen by its indicators
  for (int i = 0; i < n; i++) {
    dcp::Lin s = 0.0;
    for (int v = 0; v < n; v++) s = s + (double)v * y[i][v];
    dcp::add_row(h, x[i] - s, 0, 0);
  }

  // z[i][k] = 1 when the interval between positions i and i+1 has size k (k = 1..n-1)
  std::vector<std::vector<dcp::Lin>> z(n - 1, std::vector<dcp::Lin>(n));
  for (int i = 0; i < n - 1; i++)
    for (int k = 1; k < n; k++) z[i][k] = dcp::new_var(h, 0, 1);

  // each neighbouring pair has exactly one interval size
  for (int i = 0; i < n - 1; i++) {
    dcp::Lin s = 0.0;
    for (int k = 1; k < n; k++) s = s + z[i][k];
    dcp::add_row(h, s, 1, 1);
  }

  // the intervals cover each of 1..n-1 exactly once
  for (int k = 1; k < n; k++) {
    dcp::Lin s = 0.0;
    for (int i = 0; i < n - 1; i++) s = s + z[i][k];
    dcp::add_row(h, s, 1, 1);
  }

  // each interval diffs[i] equals the chosen interval size of its pair
  for (int i = 0; i < n - 1; i++) {
    dcp::Lin s = 0.0;
    for (int k = 1; k < n; k++) s = s + (double)k * z[i][k];
    dcp::add_row(h, diffs[i] - s, 0, 0);
  }

  // diffs[i] is the absolute difference |x[i+1] - x[i]|; the big-M is 2(n-1), since both
  // x values lie in 0..n-1, so x[i+1] - x[i] lies in -(n-1)..(n-1)
  double M = 2.0 * (n - 1);
  for (int i = 0; i < n - 1; i++) {
    // diffs[i] is at least x[i+1] - x[i] and at least x[i] - x[i+1]
    dcp::add_row(h, diffs[i] - x[i + 1] + x[i], 0, kHighsInf);
    dcp::add_row(h, diffs[i] - x[i] + x[i + 1], 0, kHighsInf);
    // a binary b chooses which of the two differences the interval equals
    dcp::Lin b = dcp::new_var(h, 0, 1);
    // when b = 1, diffs[i] <= x[i+1] - x[i]; when b = 0, that row is slack
    dcp::add_row(h, diffs[i] - x[i + 1] + x[i] + M * b, -kHighsInf, M);
    // when b = 0, diffs[i] <= x[i] - x[i+1]; when b = 1, that row is slack
    dcp::add_row(h, diffs[i] - x[i] + x[i + 1] - M * b, -kHighsInf, 0);
  }

  out.add("x", x);
  out.add("diffs", diffs);
}
