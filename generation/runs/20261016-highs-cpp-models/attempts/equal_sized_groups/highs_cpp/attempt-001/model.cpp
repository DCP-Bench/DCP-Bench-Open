// Problem: equal_sized_groups.
// Divide a sorted list of N elements into K groups by choosing K-1 split points between
// them. Equal values must stay in the same group. Find K groups as close in size to
// round(N/K) as possible: minimise the total error, the sum over groups of
// abs(size - round(N/K)). Output x: the 1-based break points.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const std::vector<int> a = instance.at("a").get<std::vector<int>>();
  const int N = static_cast<int>(a.size());
  const int K = instance.at("k").get<int>();
  // round(N/K), halves rounded up, in integers
  const int T = (2 * N + K) / (2 * K);
  const int B = K - 1;  // number of break points

  // Break j (1-based) is placed after element p (1-based), so group j ends at p.
  // y[j][p] = 1 means break j is after element p.
  // Break j is possible only at p in [j, N-K+j], so every group keeps room for at
  // least one element, and only where the value changes (equal values stay together).
  std::vector<dcp::Lin> x(B);
  for (int j = 1; j <= B; ++j) {
    // exactly one position is chosen for break j
    dcp::Lin count;
    dcp::Lin position;
    for (int p = j; p <= N - K + j; ++p) {
      if (a[p - 1] == a[p]) continue;  // element p and element p+1 have the same value
      dcp::Lin y = dcp::new_var(h, 0, 1);
      count = count + y;
      position = position + static_cast<double>(p) * y;
    }
    dcp::add_row(h, count, 1, 1);
    x[j - 1] = position;
  }

  // break points strictly increase, so every group has at least one element
  for (int j = 1; j < B; ++j) {
    dcp::add_row(h, x[j] - x[j - 1], 1, kHighsInf);
  }

  // size of each group: the gap between consecutive break points
  std::vector<dcp::Lin> sizes;
  if (B == 0) {
    sizes.push_back(dcp::Lin(N));
  } else {
    sizes.push_back(x[0]);
    for (int j = 1; j < B; ++j) sizes.push_back(x[j] - x[j - 1]);
    sizes.push_back(N - x[B - 1]);
  }

  // error of each group: e >= size - T and e >= T - size, minimised
  dcp::Lin total_error;
  for (const dcp::Lin& s : sizes) {
    dcp::Lin e = dcp::new_var(h, 0, kHighsInf, false);
    dcp::add_row(h, e - s, -T, kHighsInf);  // e - size >= -T
    dcp::add_row(h, e + s, T, kHighsInf);   // e + size >= T
    total_error = total_error + e;
  }
  out.minimize(total_error);

  out.add("x", x);
}
