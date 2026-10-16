// Giant cat army: a list of 24 integers x[0..23], each at most 60 and all distinct.
// The list starts at 0 and each next element is the previous one plus 5, the previous
// one plus 7, or the square root of the previous one (only when that is an integer).
// The list ends with 14, and 2, 10 and 14 appear on it in that order.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;  // the problem has no instance data
  using dcp::Lin;
  const int N = 24;     // length of the list
  const int MAXV = 60;  // every element is at most 60
  const int MAXR = 7;   // largest integer square root of an element at most 60

  auto sum = [](const std::vector<Lin>& terms) {
    Lin s;
    for (const auto& t : terms) s = s + t;
    return s;
  };

  // list elements, each an integer from 0 to 60
  std::vector<Lin> x;
  for (int i = 0; i < N; i++) x.push_back(dcp::new_var(h, 0, MAXV));

  // the list starts with 0 and ends with 14
  dcp::add_row(h, x[0], 0, 0);
  dcp::add_row(h, x[N - 1], 14, 14);

  // y[i][v] is 1 when element i of the list equals v
  std::vector<std::vector<Lin>> y(N);
  for (int i = 0; i < N; i++)
    for (int v = 0; v <= MAXV; v++) y[i].push_back(dcp::new_var(h, 0, 1));

  // each element is one value: x[i] equals the value its indicator selects
  for (int i = 0; i < N; i++) {
    // exactly one value is chosen for element i
    dcp::add_row(h, sum(y[i]), 1, 1);
    Lin val;
    for (int v = 0; v <= MAXV; v++) val = val + double(v) * y[i][v];
    // element i equals the chosen value
    dcp::add_row(h, x[i] - val, 0, 0);
  }

  // all the elements are distinct: each value is used at most once
  for (int v = 0; v <= MAXV; v++) {
    std::vector<Lin> at_v;
    for (int i = 0; i < N; i++) at_v.push_back(y[i][v]);
    dcp::add_row(h, sum(at_v), 0, 1);
  }

  // each step adds 5, adds 7, or takes the square root: one choice per step
  for (int i = 0; i + 1 < N; i++) {
    Lin a5 = dcp::new_var(h, 0, 1);
    Lin a7 = dcp::new_var(h, 0, 1);
    Lin as = dcp::new_var(h, 0, 1);
    // exactly one of the three operations is used for this step
    dcp::add_row(h, a5 + a7 + as, 1, 1);

    Lin diff = x[i + 1] - x[i];
    // when the step adds 5, the next element is the previous one plus 5
    // (the difference lies in -60..60, so big-M = 65)
    dcp::add_row(h, diff - 5.0 + 65.0 * a5, -kHighsInf, 65);
    dcp::add_row(h, diff - 5.0 - 65.0 * a5, -65, kHighsInf);
    // when the step adds 7, the next element is the previous one plus 7
    // (the difference lies in -60..60, so big-M = 67)
    dcp::add_row(h, diff - 7.0 + 67.0 * a7, -kHighsInf, 67);
    dcp::add_row(h, diff - 7.0 - 67.0 * a7, -67, kHighsInf);

    // when the step takes a square root, pick the integer root r with r*r = previous element
    std::vector<Lin> roots;
    for (int r = 0; r <= MAXR; r++) roots.push_back(dcp::new_var(h, 0, 1));
    // exactly one root is picked when the step takes a square root, none otherwise
    dcp::add_row(h, sum(roots) - as, 0, 0);
    Lin sq, rt;
    for (int r = 0; r <= MAXR; r++) {
      sq = sq + double(r * r) * roots[r];
      rt = rt + double(r) * roots[r];
    }
    // the previous element is the square of the picked root
    // (values lie in 0..60 and the squares lie in 0..49, so big-M = 60)
    dcp::add_row(h, x[i] - sq + 60.0 * as, -kHighsInf, 60);
    dcp::add_row(h, x[i] - sq - 60.0 * as, -60, kHighsInf);
    // the next element is the picked root
    // (the difference lies in -7..60, so big-M = 60)
    dcp::add_row(h, x[i + 1] - rt + 60.0 * as, -kHighsInf, 60);
    dcp::add_row(h, x[i + 1] - rt - 60.0 * as, -60, kHighsInf);
  }

  // 2, 10 and 14 appear on the list in that order, with other numbers allowed between them
  // the list contains 2 exactly once
  std::vector<Lin> has2, has10;
  for (int i = 0; i < N; i++) {
    has2.push_back(y[i][2]);
    has10.push_back(y[i][10]);
  }
  dcp::add_row(h, sum(has2), 1, 1);
  // the list contains 10 exactly once
  dcp::add_row(h, sum(has10), 1, 1);
  // 2 comes before 10 (the position of 10 is at least one more than the position of 2)
  Lin pos2, pos10;
  for (int i = 0; i < N; i++) {
    pos2 = pos2 + double(i) * y[i][2];
    pos10 = pos10 + double(i) * y[i][10];
  }
  dcp::add_row(h, pos10 - pos2, 1, kHighsInf);

  out.add("x", x);
}
