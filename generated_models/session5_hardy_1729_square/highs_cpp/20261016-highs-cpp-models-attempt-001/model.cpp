// Find four different numbers a, b, c, d between 1 and 100 with a^2 + b^2 = c^2 + d^2.
// Print the numbers (a, b, c, d).
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;  // the problem has no instance data: the bounds 1..100 come from the description
  const int lo = 1, hi = 100, count = 4;  // four numbers, each in 1..100

  // one-hot binaries: y[k][v] = 1 when number k (0 = a, 1 = b, 2 = c, 3 = d) takes the value v
  std::vector<std::vector<dcp::Lin>> y(count, std::vector<dcp::Lin>(hi + 1));
  for (int k = 0; k < count; ++k)
    for (int v = lo; v <= hi; ++v) y[k][v] = dcp::new_var(h, 0, 1);

  // each number takes exactly one value
  for (int k = 0; k < count; ++k) {
    // exactly one value is chosen for number k
    dcp::Lin one_value = 0;
    for (int v = lo; v <= hi; ++v) one_value = one_value + y[k][v];
    dcp::add_row(h, one_value, 1, 1);
  }

  // the four numbers are all different: each value is taken by at most one number
  for (int v = lo; v <= hi; ++v) {
    // a value is used by at most one of the four numbers
    dcp::Lin uses = 0;
    for (int k = 0; k < count; ++k) uses = uses + y[k][v];
    dcp::add_row(h, uses, -kHighsInf, 1);
  }

  // a^2 + b^2 = c^2 + d^2: the squares of the chosen values, the two first on the left
  // and the two others on the right, must balance
  dcp::Lin balance = 0;
  for (int v = lo; v <= hi; ++v) {
    double sq = static_cast<double>(v) * v;
    balance = balance + sq * (y[0][v] + y[1][v]) - sq * (y[2][v] + y[3][v]);
  }
  dcp::add_row(h, balance, 0, 0);

  // the numbers a, b, c, d are the chosen values
  dcp::Lin a = 0, b = 0, c = 0, d = 0;
  for (int v = lo; v <= hi; ++v) {
    a = a + static_cast<double>(v) * y[0][v];
    b = b + static_cast<double>(v) * y[1][v];
    c = c + static_cast<double>(v) * y[2][v];
    d = d + static_cast<double>(v) * y[3][v];
  }
  out.add("a", a);
  out.add("b", b);
  out.add("c", c);
  out.add("d", d);
}
