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

  // Break j (1-based) is placed after element x_j (1-based), so group j ends at x_j.
  // Break j lies in [first, last]: every group keeps room for at least one element.
  // u[p] = 1 means x_j > p, so x_j = first + sum of u[p] (unit coefficients only).
  // Position p is forbidden for break j when elements p and p+1 have the same value.
  std::vector<dcp::Lin> x(B);
  for (int j = 1; j <= B; ++j) {
    const int first = j;
    const int last = N - K + j;
    dcp::Lin xj = dcp::new_var(h, first, last);
    x[j - 1] = xj;

    std::vector<dcp::Lin> u;
    for (int p = first; p < last; ++p) u.push_back(dcp::new_var(h, 0, 1));

    // u[p] as an expression; outside [first, last) it is a constant
    auto U = [&](int p) -> dcp::Lin {
      if (p < first) return dcp::Lin(1);
      if (p >= last) return dcp::Lin(0);
      return u[p - first];
    };

    // the break position is first plus the number of steps taken
    dcp::Lin steps;
    for (const dcp::Lin& ui : u) steps = steps + ui;
    dcp::add_row(h, xj - steps, first, first);

    // u is non-increasing in p: once x_j <= p, it stays <= p
    for (int p = first; p + 1 < last; ++p) {
      dcp::add_row(h, U(p) - U(p + 1), 0, kHighsInf);
    }

    // equal values stay together: no break between element p and element p+1 when
    // a[p-1] == a[p]; x_j = p means u[p-1] = 1 and u[p] = 0
    for (int p = first; p <= last; ++p) {
      if (a[p - 1] != a[p]) continue;
      dcp::add_row(h, U(p - 1) - U(p), -kHighsInf, 0);
    }
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
