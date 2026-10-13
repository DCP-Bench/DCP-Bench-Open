// All-interval series: arrange the pitch classes 0..n-1 so that the neighbouring intervals are exactly 1..n-1.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");

  // x[i] is the pitch class played at position i; the series is a permutation of 0..n-1
  vec<IntVar*> x;
  createVars(x, n, 0, n - 1);
  // every pitch class occurs exactly once
  all_different(x);

  // diffs[i] is the interval between positions i and i+1, a value in 1..n-1
  vec<IntVar*> diffs;
  createVars(diffs, n - 1, 1, n - 1);
  // every interval from 1 to n-1 occurs exactly once among the neighbouring pairs
  all_different(diffs);

  // the interval between neighbours is the absolute difference of their pitch classes
  for (int i = 0; i < n - 1; ++i) {
    IntVar* delta = newIntVar(-(n - 1), n - 1);
    int_minus(x[i + 1], x[i], delta);
    int_abs(delta, diffs[i]);
  }

  // search on the pitch classes in series order, smallest first
  branch(x, VAR_INORDER, VAL_MIN);

  json series = json::array();
  for (int i = 0; i < n; ++i) series.push_back(dcp::out(x[i]));
  json intervals = json::array();
  for (int i = 0; i < n - 1; ++i) intervals.push_back(dcp::out(diffs[i]));
  outputs = {{"x", series}, {"diffs", intervals}};
}
