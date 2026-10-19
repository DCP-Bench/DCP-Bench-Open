// Bowls numbered 1 to n in a line, one meter apart. Place m oranges, at most one per bowl,
// so that no three oranges have equal spacing (no orange is the midpoint of two others).
// Output x lists the bowls holding oranges in ascending order.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int n = instance.at("n").get<int>();
  const int m = instance.at("m").get<int>();

  // y[p] = 1 when bowl p+1 holds an orange
  std::vector<dcp::Lin> y;
  for (int p = 0; p < n; ++p) y.push_back(dcp::new_var(h, 0, 1));

  // place all m oranges
  dcp::Lin total;
  for (int p = 0; p < n; ++p) total = total + y[p];
  dcp::add_row(h, total, m, m);

  // no three oranges A, B, C with the distance from A to B equal to the distance from B to C:
  // for every bowls p, p+d, p+2d, at most two of them hold an orange
  for (int d = 1; 2 * d <= n - 1; ++d)
    for (int p = 0; p + 2 * d <= n - 1; ++p)
      dcp::add_row(h, y[p] + y[p + d] + y[p + 2 * d], -kHighsInf, 2);

  // z[k][p] = 1 when the k-th orange (in ascending order) sits in bowl p+1
  std::vector<std::vector<dcp::Lin>> z(m, std::vector<dcp::Lin>(n));
  for (int k = 0; k < m; ++k)
    for (int p = 0; p < n; ++p) z[k][p] = dcp::new_var(h, 0, 1);

  // each orange index is in exactly one bowl
  for (int k = 0; k < m; ++k) {
    dcp::Lin one;
    for (int p = 0; p < n; ++p) one = one + z[k][p];
    dcp::add_row(h, one, 1, 1);
  }
  // each bowl holds an orange exactly when one index is assigned to it
  for (int p = 0; p < n; ++p) {
    dcp::Lin used;
    for (int k = 0; k < m; ++k) used = used + z[k][p];
    dcp::add_row(h, used - y[p], 0, 0);
  }

  // x[k] = bowl number of the k-th orange, which is ascending
  std::vector<dcp::Lin> x(m);
  for (int k = 0; k < m; ++k) {
    for (int p = 0; p < n; ++p) x[k] = x[k] + (p + 1) * z[k][p];
  }
  for (int k = 0; k + 1 < m; ++k) dcp::add_row(h, x[k + 1] - x[k], 1, kHighsInf);

  out.add("x", x);
}
