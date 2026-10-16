// Problem fibonacci_even: the sum of the even-valued terms of the Fibonacci sequence
// (starting 1, 2, 3, 5, 8, ...) which do not exceed four million. Output res.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;  // the problem has no instance fields
  const double LIMIT = 4000000;  // "do not exceed four million"
  const int TERMS = 36;          // term 32 (5702887) is above the limit, so later terms are too
  const double UB = 100000000;   // bound on every term; term 35 is 24157817
  const double HALF = UB / 2;

  // Term t[i] of the sequence, with t[0] = 1 and t[1] = 2.
  std::vector<dcp::Lin> t(TERMS);
  t[0] = dcp::new_var(h, 1, 1);
  t[1] = dcp::new_var(h, 2, 2);
  for (int i = 2; i < TERMS; i++) t[i] = dcp::new_var(h, 0, UB);

  // Each new term is the sum of the previous two terms.
  for (int i = 0; i + 2 < TERMS; i++) {
    dcp::add_row(h, t[i + 2] - t[i] - t[i + 1], 0, 0);
  }

  // Term i is within the limit, le[i] = 1 when t[i] <= LIMIT.
  // le[i] = 1 implies t[i] <= LIMIT.
  // le[i] = 0 implies t[i] >= LIMIT + 1.
  std::vector<dcp::Lin> le(TERMS), p(TERMS), q(TERMS), g(TERMS), v(TERMS);
  for (int i = 0; i < TERMS; i++) {
    le[i] = dcp::new_var(h, 0, 1);
    dcp::add_row(h, t[i] + UB * le[i], -kHighsInf, LIMIT + UB);
    dcp::add_row(h, t[i] + (LIMIT + 1) * le[i], LIMIT + 1, kHighsInf);
  }

  // Term i is even when p[i] = 0: t[i] = 2 q[i] + p[i].
  for (int i = 0; i < TERMS; i++) {
    p[i] = dcp::new_var(h, 0, 1);
    q[i] = dcp::new_var(h, 0, HALF);
    dcp::add_row(h, t[i] - 2 * q[i] - p[i], 0, 0);
  }

  // g[i] = 1 exactly when term i is within the limit and even: g = le AND NOT p.
  for (int i = 0; i < TERMS; i++) {
    g[i] = dcp::new_var(h, 0, 1);
    dcp::add_row(h, g[i] - le[i], -kHighsInf, 0);
    dcp::add_row(h, g[i] + p[i], -kHighsInf, 1);
    dcp::add_row(h, g[i] - le[i] + p[i], 0, kHighsInf);
  }

  // v[i] = t[i] when g[i] = 1, and 0 otherwise.
  for (int i = 0; i < TERMS; i++) {
    v[i] = dcp::new_var(h, 0, UB);
    dcp::add_row(h, v[i] - t[i], -kHighsInf, 0);
    dcp::add_row(h, v[i] - UB * g[i], -kHighsInf, 0);
    dcp::add_row(h, v[i] - t[i] - UB * g[i], -UB, kHighsInf);
  }

  // res is the sum of the even terms within the limit.
  dcp::Lin res = 0;
  for (int i = 0; i < TERMS; i++) res = res + v[i];
  out.add("res", res);
}
